"""CrewAI toolkit adapter for Cobo Agentic Wallet."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, Field, create_model

from cobo_agentic_wallet.client import WalletAPIClient
from cobo_agentic_wallet.errors import APIError, PolicyDeniedError
from cobo_agentic_wallet.integrations.crewai.tools import (
    build_tool_handler_map,
    format_denial_text,
)
from cobo_agentic_wallet.toolkit import AgentWalletToolkit, ToolDefinition, ToolHandler

try:
    from crewai.tools import BaseTool
except ImportError as exc:  # pragma: no cover - import guard
    raise ImportError(
        "crewai is required for this integration. "
        "Install with: pip install 'cobo-agentic-wallet[crewai]'"
    ) from exc

# JSON Schema type -> Python annotation mapping
_JSON_TYPE_MAP: dict[str, type] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "object": dict,
    "array": list,
    "null": type(None),
}


def _literal_annotation(values: list[Any]) -> Any:
    """Build a runtime Literal annotation from schema constants/enums."""

    return Literal.__getitem__(tuple(values))


def _camel(segments: list[str]) -> str:
    """Join snake-case / lowercase segments into PascalCase for model names."""

    return "".join(part[:1].upper() + part[1:] for part in segments if part)


def _json_schema_type_to_annotation(
    prop: dict[str, Any], model_name_hint: str | None = None
) -> Any:
    """Map a JSON Schema property to a Python type annotation.

    When ``model_name_hint`` is provided, nested ``object`` schemas that carry
    their own ``properties`` are converted into Pydantic ``BaseModel`` subclasses
    so the generated CrewAI ``args_schema`` preserves the full nested shape.
    CrewAI inlines ``args_schema.model_json_schema()`` into the tool description
    passed to the LLM (see ``BaseTool._generate_description``), so without this
    recursion the LLM would only see ``spec: object`` and be unable to construct
    valid pact specs on its own.

    When ``model_name_hint`` is omitted we fall back to ``dict[str, Any]`` so
    legacy callers (and object schemas that lack ``properties``) behave as before.
    """

    if "const" in prop:
        return _literal_annotation([prop["const"]])

    enum_values = prop.get("enum")
    if isinstance(enum_values, list) and enum_values:
        return _literal_annotation(enum_values)

    json_type = prop.get("type", "string")

    if isinstance(json_type, list):
        annotations = [_JSON_TYPE_MAP.get(item_type, Any) for item_type in json_type]
        annotation = annotations[0] if annotations else Any
        for next_annotation in annotations[1:]:
            annotation = annotation | next_annotation
        return annotation

    if json_type == "array":
        items_schema = prop.get("items")
        if isinstance(items_schema, dict):
            child_hint = f"{model_name_hint}Item" if model_name_hint else None
            item_annotation = _json_schema_type_to_annotation(items_schema, child_hint)
            return list[item_annotation]
        return list[Any]

    if json_type == "object":
        if model_name_hint is not None and isinstance(prop.get("properties"), dict):
            return _build_object_model(prop, model_name_hint)
        additional = prop.get("additionalProperties")
        if isinstance(additional, dict):
            child_hint = f"{model_name_hint}Value" if model_name_hint else None
            return dict[str, _json_schema_type_to_annotation(additional, child_hint)]
        return dict[str, Any]

    return _JSON_TYPE_MAP.get(json_type, str)


def _build_object_model(obj_schema: dict[str, Any], model_name: str) -> type[BaseModel]:
    """Build a Pydantic BaseModel from an object JSON Schema with ``properties``.

    Nested objects become their own BaseModel subclasses recursively, so that
    ``args_schema.model_json_schema()`` round-trips the canonical shape exactly.
    """

    sub_properties = obj_schema.get("properties", {})
    required_fields = set(obj_schema.get("required", []))

    field_definitions: dict[str, Any] = {}
    for name, prop in sub_properties.items():
        child_hint = f"{model_name}{_camel([name])}"
        annotation = _json_schema_type_to_annotation(prop, child_hint)
        field_kwargs = _field_constraints_from_json_schema(prop)

        if name in required_fields:
            field_definitions[name] = (annotation, Field(**field_kwargs))
        elif "default" in prop:
            field_definitions[name] = (
                annotation,
                Field(default=prop["default"], **field_kwargs),
            )
        else:
            field_definitions[name] = (
                annotation | None,
                Field(default=None, **field_kwargs),
            )

    return create_model(model_name, **field_definitions)


def _field_constraints_from_json_schema(prop: dict[str, Any]) -> dict[str, Any]:
    """Translate common JSON Schema constraints to Pydantic Field kwargs."""

    kwargs: dict[str, Any] = {}

    description = prop.get("description")
    if isinstance(description, str) and description:
        kwargs["description"] = description

    if "minimum" in prop:
        kwargs["ge"] = prop["minimum"]
    if "maximum" in prop:
        kwargs["le"] = prop["maximum"]
    if "exclusiveMinimum" in prop:
        kwargs["gt"] = prop["exclusiveMinimum"]
    if "exclusiveMaximum" in prop:
        kwargs["lt"] = prop["exclusiveMaximum"]
    if "minLength" in prop:
        kwargs["min_length"] = prop["minLength"]
    if "maxLength" in prop:
        kwargs["max_length"] = prop["maxLength"]
    if "pattern" in prop:
        kwargs["pattern"] = prop["pattern"]
    if "minItems" in prop:
        kwargs["min_length"] = prop["minItems"]
    if "maxItems" in prop:
        kwargs["max_length"] = prop["maxItems"]

    return kwargs


def build_args_schema(tool_def: ToolDefinition) -> type[BaseModel]:
    """Create a Pydantic v2 BaseModel from a ToolDefinition's JSON Schema parameters.

    The generated model is used as the ``args_schema`` for a CrewAI
    ``BaseTool``, giving it proper input validation and type hints.

    Nested ``object`` fields that declare ``properties`` are recursively
    expanded into their own Pydantic ``BaseModel`` subclasses, so CrewAI's
    auto-generated ``Tool Arguments: ...`` description (see
    ``BaseTool._generate_description``) reflects the canonical nested shape
    the LLM needs in order to construct valid pact specs, transfer fees,
    EIP-712 payloads, etc.

    Top-level ``object`` fields are still declared optional even when the
    canonical schema lists them as required. This preserves the handler-level
    ``ValueError`` guidance path: if the LLM omits ``spec`` or passes an empty
    policies list, the handler can raise a ``ValueError`` with a copy-paste
    example instead of pydantic swallowing it as a "Field required" error.
    """

    tool_camel = _camel(tool_def.name.split("_"))
    model_name = f"{tool_camel}CrewAIInput"

    properties = tool_def.parameters.get("properties", {})
    required_fields = set(tool_def.parameters.get("required", []))

    field_definitions: dict[str, Any] = {}
    for name, prop in properties.items():
        field_hint = f"{model_name}{_camel([name])}"
        annotation = _json_schema_type_to_annotation(prop, field_hint)
        field_kwargs = _field_constraints_from_json_schema(prop)

        is_required = name in required_fields and prop.get("type") != "object"
        if is_required:
            field_definitions[name] = (annotation, Field(**field_kwargs))
        elif "default" in prop:
            field_definitions[name] = (annotation, Field(default=prop["default"], **field_kwargs))
        else:
            field_definitions[name] = (annotation | None, Field(default=None, **field_kwargs))

    return create_model(model_name, **field_definitions)


def _serialize_result(payload: Any) -> str:
    """Serialize a tool result to a JSON string, passing plain strings through unchanged."""
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)


def _has_object_property(parameters: Any) -> bool:
    """Return True if the canonical parameters declare any nested object/array-of-object field.

    CrewAI's generated Pydantic ``args_schema`` flattens nested objects into
    ``dict[str, Any]``, so the LLM cannot see the inner shape from the schema
    alone. We detect this case to decide whether we should append the full
    canonical JSON Schema to the tool description as a textual fallback.
    """

    if not isinstance(parameters, dict):
        return False

    properties = parameters.get("properties")
    if not isinstance(properties, dict):
        return False

    for prop in properties.values():
        if not isinstance(prop, dict):
            continue
        prop_type = prop.get("type")
        if prop_type == "object" and isinstance(prop.get("properties"), dict):
            return True
        if prop_type == "array":
            items = prop.get("items")
            if isinstance(items, dict) and items.get("type") == "object":
                return True
    return False


def _describe_with_schema(tool_def: ToolDefinition) -> str:
    """Compose a CrewAI tool description that includes the canonical JSON Schema.

    Agno exposes the canonical ``ToolDefinition.parameters`` schema directly via
    ``function.parameters``, so its LLM sees nested shapes like
    ``spec.policies[*].rules`` in full. CrewAI's ``args_schema`` cannot express
    those shapes (see ``build_args_schema``), so we append the schema text to
    the tool description — CrewAI passes the description verbatim to the LLM
    prompt, which closes the information gap for tools like ``submit_pact``.
    """

    base = tool_def.description or ""
    if not _has_object_property(tool_def.parameters):
        return base

    schema_json = json.dumps(tool_def.parameters, sort_keys=True, ensure_ascii=True, indent=2)
    return (
        f"{base}\n\n"
        "Arguments JSON Schema (use nested object fields exactly as shown below "
        "— the tool's ``args_schema`` cannot describe nested object structure, "
        "so rely on this schema when filling object fields):\n"
        f"{schema_json}"
    )


def _error_payload(exc: APIError) -> str:
    """Format an APIError as a JSON string suitable for raising as a RuntimeError."""
    payload = {
        "error": "API_ERROR",
        "status_code": exc.status_code,
        "message": str(exc),
        "response": exc.response_body,
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)


def _create_crewai_tool(
    *,
    tool_def: ToolDefinition,
    handler: ToolHandler,
    toolkit: AgentWalletToolkit,
    owner_loop_ref: Callable[[], asyncio.AbstractEventLoop | None],
) -> BaseTool:
    """Factory: create a CrewAI ``BaseTool`` subclass from a ``ToolDefinition``.

    ``owner_loop_ref`` returns the event loop the underlying ``WalletAPIClient``
    (and any pact-scoped sub-clients) is bound to — captured when the toolkit
    was constructed. The sync ``_run`` path reuses that loop via
    ``run_coroutine_threadsafe`` so tool calls never cross event loops, even
    when CrewAI dispatches them from ``kickoff_async``'s worker thread.
    """

    args_schema = build_args_schema(tool_def)

    def _invalid_arguments_payload(tool_name: str, exc: Exception, kwargs: dict[str, Any]) -> str:
        """Mirror the OpenAI / Agno adapters' ``INVALID_TOOL_ARGUMENTS`` JSON envelope."""
        params = tool_def.parameters if isinstance(tool_def.parameters, dict) else {}
        required = params.get("required", [])
        received = sorted(k for k, v in kwargs.items() if v is not None)
        payload = {
            "error": "INVALID_TOOL_ARGUMENTS",
            "tool": tool_name,
            "message": str(exc),
            "required": required,
            "received": received,
        }
        return json.dumps(payload, sort_keys=True, ensure_ascii=True)

    async def _invoke_async(**kwargs: Any) -> str:
        try:
            result = await handler(**kwargs)
            return _serialize_result(result)
        except PolicyDeniedError as exc:
            return format_denial_text(toolkit, exc.denial)
        except APIError as exc:
            raise RuntimeError(_error_payload(exc)) from exc
        except (TypeError, ValueError) as exc:
            # Mirror the Agno adapter: surface validation errors (missing /
            # malformed kwargs, empty spec, handler-level shape checks) as a
            # structured INVALID_TOOL_ARGUMENTS envelope with required /
            # received fields. The envelope's ``message`` still carries the
            # handler's copy-pasteable example, and the structured shape helps
            # the LLM self-correct instead of giving up after one failure.
            return _invalid_arguments_payload(tool_def.name, exc, kwargs)

    def _run(self: BaseTool, **kwargs: Any) -> str:
        # We arrive here in two shapes:
        #
        # 1. Called from a plain sync context (no running loop on this thread)
        #    — either the user invoked ``kickoff`` directly, or CrewAI's
        #    ``kickoff_async`` dispatched us into a worker thread via
        #    ``asyncio.to_thread``.
        # 2. Called while a loop is already running on this thread — rare, but
        #    can happen if a user wires the tool into their own async code and
        #    mistakenly calls the sync ``invoke`` path.
        #
        # In both cases we want the coroutine to run on the SAME event loop
        # that owns the ``WalletAPIClient``'s aiohttp session. Creating a
        # fresh loop via ``asyncio.run`` (CrewAI's default behavior) leaves
        # the session bound to a now-closed loop, which manifests as
        # ``Event loop is closed`` or ``attached to a different loop`` on
        # the second/third tool call — exactly the failure we saw with
        # ``kickoff_async``.
        owner_loop = owner_loop_ref()
        if owner_loop is not None and owner_loop.is_running():
            future = asyncio.run_coroutine_threadsafe(_invoke_async(**kwargs), owner_loop)
            return future.result()

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No running loop anywhere we can schedule onto; fall back to a
            # fresh throwaway loop. This path is best-effort — it works for
            # one-shot sync ``kickoff`` usage where the caller manages the
            # client lifecycle explicitly — but users of ``kickoff_async``
            # should always hit the ``owner_loop`` branch above.
            return asyncio.run(_invoke_async(**kwargs))

        raise RuntimeError(
            "CrewAI tools are synchronous wrappers over async API calls. "
            "Call them from a sync context, or execute in a separate thread from async code."
        )

    async def _arun(self: BaseTool, **kwargs: Any) -> str:
        # Direct async path — used when CrewAI's ``CrewStructuredTool.ainvoke``
        # awaits a coroutine-typed ``func`` on the caller's loop. This is the
        # ideal path because no cross-loop scheduling is involved.
        return await _invoke_async(**kwargs)

    def _to_structured_tool(self: BaseTool):
        """Route CrewAI's StructuredTool conversion at the sync handler.

        CrewAI's ``kickoff_async`` is implemented as
        ``await asyncio.to_thread(self.kickoff, ...)`` (see
        ``crewai/crew.py::kickoff_async``) — i.e. even the "async" entrypoint
        runs the whole agent loop synchronously in a worker thread, and that
        worker thread dispatches tool calls through the sync
        ``CrewStructuredTool.invoke`` path. ``invoke`` wraps coroutine
        ``func`` values with ``asyncio.run(...)``, which spins up a fresh
        event loop per call and closes it when the tool returns, leaving
        the shared aiohttp session attached to a dead loop on the next call.
        Handing CrewAI the coroutine function directly therefore does NOT
        solve the cross-loop problem inside ``kickoff_async``.
        Handing CrewAI the sync ``_run`` wrapper does: ``_run`` reuses the
        owner loop (captured at toolkit construction) via
        ``run_coroutine_threadsafe``, so every tool call executes on the
        same loop as the ``WalletAPIClient``.
        """
        from crewai.tools.structured_tool import CrewStructuredTool

        self._set_args_schema()
        structured = CrewStructuredTool(
            name=self.name,
            description=self.description,
            args_schema=self.args_schema,
            func=self._run,
            result_as_answer=self.result_as_answer,
            max_usage_count=self.max_usage_count,
            current_usage_count=self.current_usage_count,
        )
        structured._original_tool = self
        return structured

    description = _describe_with_schema(tool_def)

    class_name = "".join(part.capitalize() for part in tool_def.name.split("_")) + "CrewAITool"
    tool_cls = type(
        class_name,
        (BaseTool,),
        {
            "__module__": __name__,
            "__annotations__": {
                "name": str,
                "description": str,
                "args_schema": type[BaseModel],
            },
            "name": tool_def.name,
            "description": description,
            "args_schema": args_schema,
            "_run": _run,
            "_arun": _arun,
            "to_structured_tool": _to_structured_tool,
            "__doc__": description,
        },
    )
    return tool_cls()


class CoboAgentWalletCrewAIToolkit:
    """CrewAI toolkit exposing Cobo Agentic Wallet tools for use with the CrewAI agent framework.

    Maps the canonical tool surface from :class:`AgentWalletToolkit` to CrewAI
    ``BaseTool`` instances with Pydantic ``args_schema`` models derived from the
    canonical JSON Schema.  Policy denials are returned as formatted strings so
    agents can self-correct without raising exceptions.
    """

    def __init__(
        self,
        *,
        client: WalletAPIClient,
        include_tools: list[str] | None = None,
        exclude_tools: list[str] | None = None,
    ) -> None:
        # Validate the canonical tool surface on an unfiltered toolkit so adapter
        # drift is caught independently from user-facing include/exclude filtering.
        canonical_toolkit = AgentWalletToolkit(client)
        build_tool_handler_map(canonical_toolkit)

        self._base_toolkit = AgentWalletToolkit(
            client,
            include_tools=include_tools,
            exclude_tools=exclude_tools,
        )
        # Capture the event loop the WalletAPIClient is bound to (typically the
        # loop that's currently running ``main()``). CrewAI's ``kickoff_async``
        # hands the agent loop off to a worker thread via ``asyncio.to_thread``
        # and then dispatches tool calls through the sync ``invoke`` path —
        # ``_run`` uses this captured loop to route coroutines back to the
        # client's owning loop instead of spawning a throwaway loop per call.
        try:
            self._owner_loop: asyncio.AbstractEventLoop | None = asyncio.get_running_loop()
        except RuntimeError:
            self._owner_loop = None
        self._handlers = {tool.name: tool.handler for tool in self._base_toolkit.get_tools()}
        self._tools = [
            _create_crewai_tool(
                tool_def=tool_def,
                handler=self._handlers[tool_def.name],
                toolkit=self._base_toolkit,
                owner_loop_ref=lambda: self._owner_loop,
            )
            for tool_def in self._base_toolkit.get_tools()
        ]

    def get_tools(self) -> list[BaseTool]:
        """Return all CrewAI BaseTool instances wrapping the Cobo Agentic Wallet API."""

        return list(self._tools)

    async def aclose(self) -> None:
        """Close any pact-scoped clients the underlying toolkit created during a run."""
        await self._base_toolkit.aclose()


__all__ = ["CoboAgentWalletCrewAIToolkit", "build_args_schema"]

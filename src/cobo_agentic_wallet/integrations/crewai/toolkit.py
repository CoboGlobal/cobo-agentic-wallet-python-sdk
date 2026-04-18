"""CrewAI toolkit adapter for Cobo Agentic Wallet."""

from __future__ import annotations

import asyncio
import json
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


def _json_schema_type_to_annotation(prop: dict[str, Any]) -> Any:
    """Map a JSON Schema property to a Python type annotation."""

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
        item_annotation = (
            _json_schema_type_to_annotation(items_schema) if isinstance(items_schema, dict) else Any
        )
        return list[item_annotation]

    if json_type == "object":
        additional = prop.get("additionalProperties")
        if isinstance(additional, dict):
            return dict[str, _json_schema_type_to_annotation(additional)]
        return dict[str, Any]

    return _JSON_TYPE_MAP.get(json_type, str)


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
    """

    properties = tool_def.parameters.get("properties", {})
    required_fields = set(tool_def.parameters.get("required", []))

    field_definitions: dict[str, Any] = {}
    for name, prop in properties.items():
        annotation = _json_schema_type_to_annotation(prop)
        field_kwargs = _field_constraints_from_json_schema(prop)

        if name in required_fields:
            field_definitions[name] = (annotation, Field(**field_kwargs))
        elif "default" in prop:
            field_definitions[name] = (annotation, Field(default=prop["default"], **field_kwargs))
        else:
            field_definitions[name] = (annotation | None, Field(default=None, **field_kwargs))

    model_name = "".join(part.capitalize() for part in tool_def.name.split("_")) + "CrewAIInput"
    return create_model(model_name, **field_definitions)


def _serialize_result(payload: Any) -> str:
    """Serialize a tool result to a JSON string, passing plain strings through unchanged."""
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)


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
) -> BaseTool:
    """Factory: create a CrewAI ``BaseTool`` subclass from a ``ToolDefinition``."""

    args_schema = build_args_schema(tool_def)

    async def _invoke_async(**kwargs: Any) -> str:
        try:
            result = await handler(**kwargs)
            return _serialize_result(result)
        except PolicyDeniedError as exc:
            return format_denial_text(toolkit, exc.denial)
        except APIError as exc:
            raise RuntimeError(_error_payload(exc)) from exc
        except ValueError as exc:
            raise RuntimeError(str(exc)) from exc

    def _run(self: BaseTool, **kwargs: Any) -> str:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(_invoke_async(**kwargs))

        raise RuntimeError(
            "CrewAI tools are synchronous wrappers over async API calls. "
            "Call them from a sync context, or execute in a separate thread from async code."
        )

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
            "description": tool_def.description,
            "args_schema": args_schema,
            "_run": _run,
            "__doc__": tool_def.description,
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
        self._handlers = {tool.name: tool.handler for tool in self._base_toolkit.get_tools()}
        self._tools = [
            _create_crewai_tool(
                tool_def=tool_def,
                handler=self._handlers[tool_def.name],
                toolkit=self._base_toolkit,
            )
            for tool_def in self._base_toolkit.get_tools()
        ]

    def get_tools(self) -> list[BaseTool]:
        """Return all CrewAI BaseTool instances wrapping the Cobo Agentic Wallet API."""

        return list(self._tools)


__all__ = ["CoboAgentWalletCrewAIToolkit", "build_args_schema"]

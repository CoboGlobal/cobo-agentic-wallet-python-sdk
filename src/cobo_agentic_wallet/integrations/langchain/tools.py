"""LangChain integration helpers for Cobo Agentic Wallet tools."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, create_model

from cobo_agentic_wallet.toolkit import AgentWalletToolkit, ToolDefinition, ToolHandler

EXPECTED_TOOL_NAMES: tuple[str, ...] = (
    "list_wallets",
    "get_wallet",
    "list_wallet_addresses",
    "get_balance",
    "submit_pact",
    "get_pact",
    "list_pacts",
    "transfer_tokens",
    "contract_call",
    "message_sign",
    "payment",
    "estimate_transfer_fee",
    "estimate_contract_call_fee",
    "list_transactions",
    "list_transaction_records",
    "get_transaction_record",
    "get_transaction_record_by_request_id",
    "list_recent_addresses",
    "get_audit_logs",
    "create_delegation",
)

# JSON Schema type → Python annotation mapping
_JSON_TYPE_MAP: dict[str, type] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "object": dict,
    "array": list,
    "null": type(None),
}


def build_tool_handler_map(toolkit: AgentWalletToolkit) -> dict[str, ToolHandler]:
    """Build a name-to-handler map from the toolkit and validate the tool surface.

    Args:
        toolkit: An initialised AgentWalletToolkit instance.

    Returns:
        A dict mapping each tool name to its callable ToolHandler.

    Raises:
        RuntimeError: If the set of tools returned by the toolkit does not
            exactly match EXPECTED_TOOL_NAMES (tools are missing or unexpected).
    """

    handlers = {tool.name: tool.handler for tool in toolkit.get_tools()}
    found = set(handlers.keys())
    missing = sorted(set(EXPECTED_TOOL_NAMES).difference(found))
    extra = sorted(found.difference(EXPECTED_TOOL_NAMES))

    if missing or extra:
        raise RuntimeError(
            f"Tool surface mismatch for LangChain integration: missing={missing}, extra={extra}"
        )

    return handlers


def format_denial_text(toolkit: AgentWalletToolkit, denial: Any) -> str:
    """Render a policy denial as human-readable text suitable for LLM self-correction.

    Args:
        toolkit: An initialised AgentWalletToolkit instance used to format the denial.
        denial: The denial object returned by a tool call that was blocked by policy.

    Returns:
        A plain-text string describing the denial reason, intended to be fed back
        to the LLM so it can revise its request.
    """

    return toolkit._format_denial(denial)


def _literal_annotation(values: list[Any]) -> Any:
    """Build a runtime Literal annotation from a list of schema const/enum values."""

    return Literal.__getitem__(tuple(values))


def _camel(segments: list[str]) -> str:
    """Join snake-case / lowercase segments into PascalCase for model names."""

    return "".join(part[:1].upper() + part[1:] for part in segments if part)


def _json_schema_type_to_annotation(
    prop: dict[str, Any], model_name_hint: str | None = None
) -> Any:
    """Derive a Python type annotation from a JSON Schema property dict.

    When ``model_name_hint`` is provided, nested ``object`` schemas that carry
    their own ``properties`` are converted into Pydantic ``BaseModel`` subclasses
    so the generated ``args_schema`` preserves the full nested shape. LangChain
    forwards ``args_schema.model_json_schema()`` to the LLM as the tool's
    parameter schema, so without this recursion the LLM would only see
    ``spec: object`` / ``dict[str, Any]`` and would be unable to construct
    valid pact specs on its own (resulting in empty-spec calls that trigger
    handler-level ``ValueError`` and abort the agent under LangGraph).

    When ``model_name_hint`` is omitted we fall back to ``dict[str, Any]`` so
    legacy callers (and object schemas that lack ``properties``) behave as
    before.
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
    """Translate common JSON Schema constraints into Pydantic v2 Field keyword arguments."""

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

    # Pydantic uses min_length/max_length for sequences.
    if "minItems" in prop:
        kwargs["min_length"] = prop["minItems"]
    if "maxItems" in prop:
        kwargs["max_length"] = prop["maxItems"]

    return kwargs


def build_args_schema(tool_def: ToolDefinition) -> type:
    """Create a Pydantic v2 BaseModel from a ToolDefinition's JSON Schema parameters.

    The generated model is used as the ``args_schema`` for a LangChain
    ``StructuredTool``, giving it proper input validation and type hints.

    Nested ``object`` fields that declare ``properties`` are recursively
    expanded into their own Pydantic ``BaseModel`` subclasses, so the schema
    LangChain forwards to the LLM reflects the canonical nested shape (e.g.
    ``spec.policies[*].rules.when.chain_in``). Without this recursion the
    LLM only sees ``spec: object`` / ``dict[str, Any]`` and tends to call
    ``submit_pact`` with an empty / missing spec, triggering a handler-level
    ``ValueError`` that LangGraph surfaces as a hard abort.

    Top-level ``object`` fields are still declared optional even when the
    canonical schema lists them as required. This preserves the handler-level
    ``ValueError`` guidance path: if the LLM omits ``spec`` entirely, the
    handler can raise a ``ValueError`` with a copy-paste example instead of
    pydantic swallowing it as a generic "Field required" error.
    """

    model_name = "".join(part.capitalize() for part in tool_def.name.split("_")) + "Input"

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


__all__ = [
    "EXPECTED_TOOL_NAMES",
    "build_tool_handler_map",
    "format_denial_text",
    "build_args_schema",
]

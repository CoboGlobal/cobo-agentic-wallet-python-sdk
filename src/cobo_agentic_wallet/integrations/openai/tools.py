"""OpenAI Agents SDK tool adapters for Cobo Agentic Wallet."""

from __future__ import annotations

import json
from typing import Any, Callable

from cobo_agentic_wallet.errors import APIError, PolicyDeniedError
from cobo_agentic_wallet.toolkit import AgentWalletToolkit, ToolDefinition, ToolHandler

try:
    from agents import FunctionTool
    from agents.tool import ToolContext
except Exception as exc:  # pragma: no cover - import guard
    # Catch all exceptions (not just ImportError) to handle cases where
    # the package is installed but fails during import (e.g., ValidationError)
    raise ImportError(
        "openai-agents is required for this integration. "
        f"Install with: pip install 'cobo-agentic-wallet[openai]'. Original error: {exc}"
    ) from exc

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

DenialRecorder = Callable[[Any, str], None]


def build_tool_handler_map(toolkit: AgentWalletToolkit) -> dict[str, ToolHandler]:
    """Build a name->handler map and validate the canonical tool surface.

    Raises:
        RuntimeError: If the toolkit's tool names do not exactly match
            ``EXPECTED_TOOL_NAMES`` (any missing or unexpected tool).
    """

    handlers = {tool.name: tool.handler for tool in toolkit.get_tools()}
    found = set(handlers.keys())
    missing = sorted(set(EXPECTED_TOOL_NAMES).difference(found))
    extra = sorted(found.difference(EXPECTED_TOOL_NAMES))

    if missing or extra:
        raise RuntimeError(
            f"Tool surface mismatch for OpenAI integration: missing={missing}, extra={extra}"
        )

    return handlers


def format_denial_text(toolkit: AgentWalletToolkit, denial: Any) -> str:
    """Render a policy denial in a text format suitable for LLM self-correction."""

    return toolkit._format_denial(denial)


def get_tool_definitions(toolkit: AgentWalletToolkit) -> list[dict[str, Any]]:
    """Return OpenAI-compatible tool metadata derived from canonical ToolDefinitions."""

    return [
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        }
        for tool in toolkit.get_tools()
    ]


def _serialize_result(payload: Any) -> str:
    """Serialize a tool result to a JSON string, passing through plain strings unchanged."""
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)


def _error_payload(exc: APIError) -> str:
    """Format an APIError as a JSON string suitable for returning to the LLM."""
    payload = {
        "error": "API_ERROR",
        "status_code": exc.status_code,
        "message": str(exc),
        "response": exc.response_body,
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)


def _create_function_tool(
    *,
    toolkit: AgentWalletToolkit,
    tool_def: ToolDefinition,
    handler: ToolHandler,
    denial_recorder: DenialRecorder | None = None,
) -> FunctionTool:
    """Wrap a single ToolDefinition and its handler in an OpenAI FunctionTool."""

    async def on_invoke_tool(ctx: ToolContext[Any], args_json: str) -> str:
        try:
            raw_args = json.loads(args_json) if args_json else {}
        except json.JSONDecodeError:
            return "Tool arguments must be valid JSON."

        if not isinstance(raw_args, dict):
            return "Tool arguments must decode to a JSON object."

        try:
            result = await handler(**raw_args)
            return _serialize_result(result)
        except PolicyDeniedError as exc:
            denial_text = format_denial_text(toolkit, exc.denial)
            if denial_recorder is not None:
                denial_recorder(getattr(ctx, "context", None), denial_text)
            return denial_text
        except APIError as exc:
            return _error_payload(exc)
        except ValueError as exc:
            return str(exc)
        except TypeError as exc:
            required = (
                tool_def.parameters.get("required", [])
                if isinstance(tool_def.parameters, dict)
                else []
            )
            return json.dumps(
                {
                    "error": "INVALID_TOOL_ARGUMENTS",
                    "tool": tool_def.name,
                    "message": str(exc),
                    "required": required,
                    "received": sorted(raw_args.keys()),
                },
                sort_keys=True,
                ensure_ascii=True,
            )

    return FunctionTool(
        name=tool_def.name,
        description=tool_def.description,
        params_json_schema=tool_def.parameters,
        on_invoke_tool=on_invoke_tool,
        # Canonical tool schemas include dynamic-object params (e.g. create_delegation.policies),
        # so strict mode must be disabled to preserve that contract.
        strict_json_schema=False,
    )


def build_function_tools(
    toolkit: AgentWalletToolkit,
    *,
    denial_recorder: DenialRecorder | None = None,
) -> list[FunctionTool]:
    """Build OpenAI FunctionTool objects from canonical ToolDefinitions.

    The supplied ``toolkit`` may already be filtered via ``include_tools`` /
    ``exclude_tools``. Canonical surface validation is done by the adapter
    entry point (``get_cobo_tools``) against an unfiltered toolkit, so this
    function intentionally avoids calling ``build_tool_handler_map`` here.
    """

    handlers = {tool.name: tool.handler for tool in toolkit.get_tools()}
    return [
        _create_function_tool(
            toolkit=toolkit,
            tool_def=tool_def,
            handler=handlers[tool_def.name],
            denial_recorder=denial_recorder,
        )
        for tool_def in toolkit.get_tools()
    ]


__all__ = [
    "EXPECTED_TOOL_NAMES",
    "build_function_tools",
    "build_tool_handler_map",
    "format_denial_text",
    "get_tool_definitions",
]

"""CrewAI integration helpers for Cobo Agentic Wallet tools."""

from __future__ import annotations

from typing import Any

from cobo_agentic_wallet.toolkit import AgentWalletToolkit, ToolHandler

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
            f"Tool surface mismatch for CrewAI integration: missing={missing}, extra={extra}"
        )

    return handlers


def format_denial_text(toolkit: AgentWalletToolkit, denial: Any) -> str:
    """Render a policy denial in a text format suitable for LLM self-correction."""

    return toolkit._format_denial(denial)


__all__ = [
    "EXPECTED_TOOL_NAMES",
    "build_tool_handler_map",
    "format_denial_text",
]

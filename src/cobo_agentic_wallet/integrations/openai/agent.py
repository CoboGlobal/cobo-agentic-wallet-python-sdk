"""OpenAI Agents SDK helper for Cobo Agentic Wallet."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from cobo_agentic_wallet.client import WalletAPIClient
from cobo_agentic_wallet.integrations.openai.tools import (
    build_function_tools,
    build_tool_handler_map,
)
from cobo_agentic_wallet.toolkit import AgentWalletToolkit

try:
    from agents import Agent
    from agents.run_context import RunContextWrapper
    from agents.tool import FunctionTool
except Exception as exc:  # pragma: no cover - import guard
    # Catch all exceptions (not just ImportError) to handle cases where
    # the package is installed but fails during import (e.g., ValidationError)
    raise ImportError(
        "openai-agents is required for this integration. "
        f"Install with: pip install 'cobo-agentic-wallet[openai]'. Original error: {exc}"
    ) from exc


@dataclass
class CoboOpenAIAgentContext:
    """Mutable run context threaded through a single OpenAI Agents SDK run.

    Accumulates wallet-policy denial messages so that the dynamic
    instructions callback can surface the latest denial to the agent.
    """

    denial_messages: list[str] = field(default_factory=list)

    @property
    def last_policy_denial(self) -> str | None:
        """Return the most recent policy denial message, or None if there are none."""
        if not self.denial_messages:
            return None
        return self.denial_messages[-1]


def create_cobo_agent_context() -> CoboOpenAIAgentContext:
    """Create a default run context object for ``create_cobo_agent``."""

    return CoboOpenAIAgentContext()


def _record_policy_denial(context: Any, denial_text: str) -> None:
    """Append a policy denial message to the run context."""
    if context is None:
        return

    denial_messages = getattr(context, "denial_messages", None)
    if isinstance(denial_messages, list):
        denial_messages.append(denial_text)
        return

    # Best-effort fallback for custom contexts.
    if hasattr(context, "last_policy_denial"):
        setattr(context, "last_policy_denial", denial_text)


def _build_instructions(
    *,
    base_instructions: str,
) -> Callable[[RunContextWrapper[Any], Agent[Any]], str]:
    """Return a dynamic instructions callable that appends the latest policy denial."""

    def _instructions(wrapper: RunContextWrapper[Any], _agent: Agent[Any]) -> str:
        context = getattr(wrapper, "context", None)
        latest_denial: str | None = None

        if context is not None:
            denial_messages = getattr(context, "denial_messages", None)
            if isinstance(denial_messages, list) and denial_messages:
                latest_denial = str(denial_messages[-1])
            else:
                fallback_denial = getattr(context, "last_policy_denial", None)
                if isinstance(fallback_denial, str) and fallback_denial:
                    latest_denial = fallback_denial

        if not latest_denial:
            return base_instructions

        return (
            f"{base_instructions}\n\n"
            "Latest wallet policy denial guidance from previous tool execution:\n"
            f"{latest_denial}\n\n"
            "If you retry, strictly follow the denial suggestion."
        )

    return _instructions


def get_cobo_tools(
    client: WalletAPIClient,
    *,
    include_tools: list[str] | None = None,
    exclude_tools: list[str] | None = None,
) -> list[FunctionTool]:
    """Return OpenAI FunctionTool instances for all canonical Cobo wallet tools."""

    # Validate the canonical tool surface on an unfiltered toolkit so adapter
    # drift is caught independently from user-facing include/exclude filtering.
    canonical_toolkit = AgentWalletToolkit(client)
    build_tool_handler_map(canonical_toolkit)

    base_toolkit = AgentWalletToolkit(
        client,
        include_tools=include_tools,
        exclude_tools=exclude_tools,
    )
    return build_function_tools(base_toolkit, denial_recorder=_record_policy_denial)


def create_cobo_agent(
    client: WalletAPIClient,
    *,
    name: str = "cobo-wallet-agent",
    model: str | Any | None = "gpt-4.1-mini",
    instructions: str | None = None,
    include_tools: list[str] | None = None,
    exclude_tools: list[str] | None = None,
    **agent_kwargs: Any,
) -> Agent[Any]:
    """Create an OpenAI Agent preconfigured with all Cobo wallet tools.

    The agent is given a dynamic instructions callback that automatically
    appends the latest wallet-policy denial message whenever one is recorded
    during the run, prompting the model to retry with compliant parameters.

    Args:
        client: Authenticated Cobo API client used to build the tool set.
        name: Display name for the agent; defaults to ``'cobo-wallet-agent'``.
        model: OpenAI model identifier or model object. Pass ``None`` to omit
            the field and rely on the SDK default. Defaults to ``'gpt-4.1-mini'``.
        instructions: Custom system instructions. When omitted, a built-in
            wallet-operator prompt is used.
        include_tools: Optional allowlist of canonical CAW tool names to expose.
        exclude_tools: Optional denylist of canonical CAW tool names to hide.
        **agent_kwargs: Additional keyword arguments forwarded verbatim to
            ``agents.Agent``.

    Returns:
        A fully configured ``agents.Agent`` instance ready to run.
    """

    tools = get_cobo_tools(
        client,
        include_tools=include_tools,
        exclude_tools=exclude_tools,
    )
    resolved_instructions = instructions or (
        "You are a wallet operator. Use Cobo wallet tools for all balance, transfer, "
        "audit, delegation, and policy tasks. If a transfer is denied by policy, read "
        "the denial details and retry with compliant parameters."
    )

    resolved_agent_kwargs: dict[str, Any] = {
        "name": name,
        "instructions": _build_instructions(base_instructions=resolved_instructions),
        "tools": tools,
    }
    if model is not None:
        resolved_agent_kwargs["model"] = model
    resolved_agent_kwargs.update(agent_kwargs)
    return Agent(**resolved_agent_kwargs)


__all__ = [
    "CoboOpenAIAgentContext",
    "create_cobo_agent",
    "create_cobo_agent_context",
    "get_cobo_tools",
]

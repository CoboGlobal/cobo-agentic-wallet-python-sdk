"""LangChain toolkit adapter for Cobo Agentic Wallet."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from pydantic import ConfigDict, PrivateAttr

from cobo_agentic_wallet.errors import APIError, PolicyDeniedError
from cobo_agentic_wallet.integrations.langchain.tools import (
    build_args_schema,
    build_tool_handler_map,
    format_denial_text,
)
from cobo_agentic_wallet.toolkit import AgentWalletToolkit, ToolDefinition, ToolHandler

try:
    from langchain_core.tools import BaseTool, BaseToolkit, StructuredTool, ToolException
except ImportError as exc:  # pragma: no cover - import guard
    raise ImportError(
        "langchain-core is required for this integration. "
        "Install with: pip install 'cobo-agentic-wallet[langchain]'"
    ) from exc


def _create_tool(
    tool_def: ToolDefinition,
    handler: ToolHandler,
    toolkit: AgentWalletToolkit,
) -> StructuredTool:
    """Factory: create a LangChain ``StructuredTool`` from a ``ToolDefinition``."""

    args_schema = build_args_schema(tool_def)

    def _serialize_result(payload: Any) -> str:
        if isinstance(payload, str):
            return payload
        return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)

    def _error_payload(exc: APIError) -> str:
        payload = {
            "error": "API_ERROR",
            "status_code": exc.status_code,
            "message": str(exc),
            "response": exc.response_body,
        }
        return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)

    async def _arun(**kwargs: Any) -> str:
        try:
            result = await handler(**kwargs)
            return _serialize_result(result)
        except PolicyDeniedError as exc:
            return format_denial_text(toolkit, exc.denial)
        except APIError as exc:
            raise ToolException(_error_payload(exc)) from exc
        except ValueError as exc:
            raise ToolException(str(exc)) from exc

    def _run_with_denial(**kwargs: Any) -> str:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            try:
                result = asyncio.run(handler(**kwargs))
                return _serialize_result(result)
            except PolicyDeniedError as exc:
                return format_denial_text(toolkit, exc.denial)
            except APIError as exc:
                raise ToolException(_error_payload(exc)) from exc
            except ValueError as exc:
                raise ToolException(str(exc)) from exc

        raise ToolException(
            "Synchronous LangChain tool call was invoked from an async event loop. "
            "Call them from a sync context, or use the async interface."
        )

    return StructuredTool(
        name=tool_def.name,
        description=tool_def.description,
        args_schema=args_schema,
        func=_run_with_denial,
        coroutine=_arun,
    )


class CoboAgentWalletToolkit(BaseToolkit):
    """LangChain toolkit wrapper over :class:`AgentWalletToolkit`.

    This adapter maps the canonical Cobo tool surface to LangChain
    ``StructuredTool`` instances with proper ``args_schema`` models.
    Policy denials are returned as formatted strings (not exceptions)
    so agents can self-correct.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: Any
    include_tools: list[str] | None = None
    exclude_tools: list[str] | None = None
    _tools: list[BaseTool] = PrivateAttr(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        # Validate the canonical tool surface on an unfiltered toolkit so adapter
        # drift is caught independently from user-facing include/exclude filtering.
        canonical_toolkit = AgentWalletToolkit(self.client)
        build_tool_handler_map(canonical_toolkit)

        base_toolkit = AgentWalletToolkit(
            self.client,
            include_tools=self.include_tools,
            exclude_tools=self.exclude_tools,
        )
        handlers = {tool.name: tool.handler for tool in base_toolkit.get_tools()}
        self._tools = [
            _create_tool(tool_def, handlers[tool_def.name], base_toolkit)
            for tool_def in base_toolkit.get_tools()
        ]

    def get_tools(self) -> list[BaseTool]:
        """Return all LangChain tools wrapping the Cobo Agentic Wallet API."""
        return list(self._tools)


__all__ = ["CoboAgentWalletToolkit"]

"""LangChain toolkit adapter for Cobo Agentic Wallet."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, PrivateAttr

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

    def _unwrap_pydantic(value: Any) -> Any:
        """Recursively convert Pydantic ``BaseModel`` instances back to plain Python.

        LangChain's ``StructuredTool`` validates tool inputs against our
        recursive ``args_schema`` (see ``build_args_schema``), which converts
        nested object fields into ``BaseModel`` subclasses for LLM schema
        fidelity. The canonical handlers, however, are declared with
        ``dict[str, Any]`` / ``list`` parameter types and perform
        ``isinstance(x, dict)`` checks — a ``SubmitPactInputSpec`` instance
        fails those checks even though it carries the right data. We dump
        BaseModel values back to plain dicts before invoking the handler so
        the handler contract stays intact and the LLM-visible schema stays
        fully nested.
        """
        if isinstance(value, BaseModel):
            return value.model_dump(exclude_none=True)
        if isinstance(value, list):
            return [_unwrap_pydantic(item) for item in value]
        if isinstance(value, dict):
            return {key: _unwrap_pydantic(item) for key, item in value.items()}
        return value

    def _error_payload(exc: APIError) -> str:
        payload = {
            "error": "API_ERROR",
            "status_code": exc.status_code,
            "message": str(exc),
            "response": exc.response_body,
        }
        return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)

    def _handle_api_error(exc: APIError) -> str:
        """Surface 4xx as a JSON ``ToolMessage`` for self-correction, re-raise 5xx.

        4xx responses from the Cobo API almost always carry an actionable
        pydantic validation error or policy-shape hint in ``response_body``
        (e.g. "ALLOW transfer policy must define when.* conditions"). Raising
        ``ToolException`` here means LangGraph's default ``tool_node`` handler
        will re-raise the exception and terminate the agent before the LLM
        ever sees that guidance — exactly the failure mode we hit on
        ``submit_pact`` when the model forgot ``when.*``. Returning the same
        payload as a JSON string instead lets LangChain feed it back as a
        ``ToolMessage`` so the model can read the error and retry (mirroring
        the ``PolicyDeniedError`` / ``INVALID_TOOL_ARGUMENTS`` paths).

        5xx errors are transient / server-side and not something the LLM can
        fix by rewriting its tool arguments, so we preserve the "raise and
        let the agent stop" behavior for those.
        """
        if 400 <= (exc.status_code or 0) < 500:
            return _error_payload(exc)
        raise ToolException(_error_payload(exc)) from exc

    def _invalid_arguments_payload(exc: Exception, kwargs: dict[str, Any]) -> str:
        """Mirror the Agno / OpenAI / CrewAI adapters' ``INVALID_TOOL_ARGUMENTS`` envelope.

        LangGraph's default ``tool_node`` error handling re-raises exceptions,
        which turns a recoverable "missing spec" argument mistake into an agent
        abort. Returning a structured JSON string instead lets LangChain feed
        the error back to the LLM as a ``ToolMessage``, so the model can read
        the guidance (the handler's copy-paste example) and retry with a valid
        payload — the same self-correction path Agno and CrewAI rely on.
        """
        params = tool_def.parameters if isinstance(tool_def.parameters, dict) else {}
        required = params.get("required", [])
        received = sorted(k for k, v in kwargs.items() if v is not None)
        payload = {
            "error": "INVALID_TOOL_ARGUMENTS",
            "tool": tool_def.name,
            "message": str(exc),
            "required": required,
            "received": received,
        }
        return json.dumps(payload, sort_keys=True, ensure_ascii=True)

    async def _arun(**kwargs: Any) -> str:
        plain_kwargs = {key: _unwrap_pydantic(value) for key, value in kwargs.items()}
        try:
            result = await handler(**plain_kwargs)
            return _serialize_result(result)
        except PolicyDeniedError as exc:
            return format_denial_text(toolkit, exc.denial)
        except APIError as exc:
            return _handle_api_error(exc)
        except (TypeError, ValueError) as exc:
            return _invalid_arguments_payload(exc, plain_kwargs)

    def _run_with_denial(**kwargs: Any) -> str:
        plain_kwargs = {key: _unwrap_pydantic(value) for key, value in kwargs.items()}
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            try:
                result = asyncio.run(handler(**plain_kwargs))
                return _serialize_result(result)
            except PolicyDeniedError as exc:
                return format_denial_text(toolkit, exc.denial)
            except APIError as exc:
                return _handle_api_error(exc)
            except (TypeError, ValueError) as exc:
                return _invalid_arguments_payload(exc, plain_kwargs)

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
    _base_toolkit: AgentWalletToolkit | None = PrivateAttr(default=None)

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
        self._base_toolkit = base_toolkit
        handlers = {tool.name: tool.handler for tool in base_toolkit.get_tools()}
        self._tools = [
            _create_tool(tool_def, handlers[tool_def.name], base_toolkit)
            for tool_def in base_toolkit.get_tools()
        ]

    def get_tools(self) -> list[BaseTool]:
        """Return all LangChain tools wrapping the Cobo Agentic Wallet API."""
        return list(self._tools)

    async def aclose(self) -> None:
        """Close any pact-scoped clients the underlying toolkit created during a run."""
        if self._base_toolkit is not None:
            await self._base_toolkit.aclose()


__all__ = ["CoboAgentWalletToolkit"]

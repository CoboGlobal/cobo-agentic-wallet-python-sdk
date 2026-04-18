"""SDK-hosted MCP stdio server for Cobo Agentic Wallet."""

from __future__ import annotations

import asyncio
import inspect
import json
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncContextManager, AsyncIterator, Awaitable, Callable, Mapping, Protocol

from cobo_agentic_wallet.client import WalletAPIClient
from cobo_agentic_wallet.errors import APIError, PolicyDeniedError
from cobo_agentic_wallet_api.exceptions import ApiException
from cobo_agentic_wallet.mcp.compat import ensure_fastmcp_compat
from cobo_agentic_wallet.tool_specs import list_tool_specs
from cobo_agentic_wallet.toolkit import AgentWalletToolkit

ensure_fastmcp_compat()

try:
    from fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - import guard
    raise ImportError(
        "fastmcp is required for the MCP server. Install with: pip install 'cobo-agentic-wallet[mcp]'"
    ) from exc


AGENT_WALLET_API_URL = "AGENT_WALLET_API_URL"
AGENT_WALLET_API_KEY = "AGENT_WALLET_API_KEY"
AGENT_WALLET_TIMEOUT = "AGENT_WALLET_TIMEOUT"
AGENT_WALLET_INCLUDE_TOOLS = "AGENT_WALLET_INCLUDE_TOOLS"
AGENT_WALLET_EXCLUDE_TOOLS = "AGENT_WALLET_EXCLUDE_TOOLS"


@dataclass(frozen=True)
class MCPServerConfig:
    """Immutable runtime configuration for the Cobo Agentic Wallet MCP stdio server."""

    api_url: str = "http://localhost:8000"
    timeout: float = 30.0
    api_key: str | None = None
    include_tools: tuple[str, ...] | None = None
    exclude_tools: tuple[str, ...] = ()

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> MCPServerConfig:
        """Construct an MCPServerConfig from environment variables.

        Args:
            env: Optional mapping to read from; defaults to ``os.environ``.

        Returns:
            An ``MCPServerConfig`` populated from ``AGENT_WALLET_API_URL``,
            ``AGENT_WALLET_API_KEY``, ``AGENT_WALLET_TIMEOUT``,
            ``AGENT_WALLET_INCLUDE_TOOLS``, and ``AGENT_WALLET_EXCLUDE_TOOLS``.

        Raises:
            ValueError: If ``AGENT_WALLET_TIMEOUT`` is not a non-negative float.
        """
        source = env or os.environ
        timeout = _parse_float(
            source.get(AGENT_WALLET_TIMEOUT),
            AGENT_WALLET_TIMEOUT,
            default=30.0,
        )
        return cls(
            api_url=source.get(AGENT_WALLET_API_URL, "http://localhost:8000"),
            timeout=timeout,
            api_key=source.get(AGENT_WALLET_API_KEY),
            include_tools=_parse_csv_list(source.get(AGENT_WALLET_INCLUDE_TOOLS)),
            exclude_tools=_parse_csv_list(source.get(AGENT_WALLET_EXCLUDE_TOOLS)) or (),
        )


def _parse_float(raw: str | None, env_key: str, *, default: float) -> float:
    """Parse a non-negative float from a raw string, returning default when raw is None."""
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{env_key} must be a float, got: {raw!r}") from exc
    if value < 0:
        raise ValueError(f"{env_key} must be >= 0, got: {raw!r}")
    return value


def _parse_csv_list(raw: str | None) -> tuple[str, ...] | None:
    """Parse a comma-separated environment variable into an ordered tuple."""
    if raw is None:
        return None
    values = tuple(part.strip() for part in raw.split(",") if part.strip())
    return values or ()


def _python_type_annotation(
    property_schema: dict[str, Any],
    *,
    required: bool,
    default: Any,
    has_default: bool,
) -> Any:
    """Derive a Python type annotation from a JSON Schema property dict."""
    schema_type = property_schema.get("type")
    if schema_type == "string":
        annotation: Any = str
    elif schema_type == "integer":
        annotation = int
    elif schema_type == "boolean":
        annotation = bool
    elif schema_type == "object":
        annotation = dict[str, Any]
    elif schema_type == "array":
        items = property_schema.get("items")
        item_type = items.get("type") if isinstance(items, dict) else None
        annotation = list[str] if item_type == "string" else list[Any]
    else:
        annotation = Any

    default_is_none = has_default and default is None
    if (not required and not has_default) or default_is_none:
        return annotation | None
    return annotation


def _build_tool_wrapper(
    tool_name: str,
    parameters_schema: dict[str, Any],
    invoke_tool: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:
    """Build a typed async wrapper function suitable for registration with FastMCP.

    Constructs an ``async def`` function whose ``__signature__`` and
    ``__annotations__`` mirror the tool's JSON Schema so that FastMCP can
    perform automatic argument validation and documentation generation.

    Args:
        tool_name: The tool identifier used as the wrapper's ``__name__``.
        parameters_schema: The ``parameters`` dict from a ``ToolSpec``, which
            must be a JSON Schema object with a ``properties`` key.
        invoke_tool: Async callable that executes the tool given its name and
            keyword arguments.

    Returns:
        An async callable with a fully typed ``inspect.Signature``.

    Raises:
        ValueError: If ``parameters_schema`` does not define object properties.
    """
    properties = parameters_schema.get("properties")
    if not isinstance(properties, dict):
        raise ValueError(f"Tool '{tool_name}' must define object properties.")

    required_list = parameters_schema.get("required") or []
    required_names = [
        name for name in required_list if isinstance(name, str) and name in properties
    ]
    required_set = set(required_names)
    optional_names = [name for name in properties if name not in required_set]
    ordered_names = [*required_names, *optional_names]

    signature_params: list[inspect.Parameter] = []
    annotations: dict[str, Any] = {}
    for arg_name in ordered_names:
        raw_schema = properties.get(arg_name)
        property_schema = raw_schema if isinstance(raw_schema, dict) else {}
        has_default = "default" in property_schema
        default = property_schema.get("default")
        annotation = _python_type_annotation(
            property_schema,
            required=arg_name in required_set,
            default=default,
            has_default=has_default,
        )
        annotations[arg_name] = annotation
        if arg_name in required_set:
            signature_params.append(
                inspect.Parameter(
                    name=arg_name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    annotation=annotation,
                )
            )
            continue

        signature_params.append(
            inspect.Parameter(
                name=arg_name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation=annotation,
                default=default if has_default else None,
            )
        )

    async def _wrapper(**kwargs: Any) -> Any:
        return await invoke_tool(tool_name, **kwargs)

    _wrapper.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
        parameters=signature_params,
        return_annotation=Any,
    )
    annotations["return"] = Any
    _wrapper.__annotations__ = annotations
    _wrapper.__name__ = tool_name
    _wrapper.__doc__ = f"MCP wrapper for '{tool_name}'."
    return _wrapper


class ClientFactory(Protocol):
    """Constructs the SDK client context used by the MCP server."""

    def __call__(
        self,
        api_key: str,
        config: MCPServerConfig,
    ) -> AsyncContextManager[WalletAPIClient]: ...


@asynccontextmanager
async def _default_client_factory(
    api_key: str,
    config: MCPServerConfig,
) -> AsyncIterator[WalletAPIClient]:
    """Create and yield a ``WalletAPIClient``, closing it on exit."""
    client = WalletAPIClient(
        base_url=config.api_url,
        api_key=api_key,
        timeout=config.timeout,
    )
    try:
        yield client
    finally:
        await client.close()


class AgentWalletMCPServer:
    """FastMCP stdio server that exposes Cobo Agentic Wallet tools over the MCP protocol.

    Lazily initialises a ``WalletAPIClient`` on the first tool invocation and
    caches it for the lifetime of the server. Use ``create_server()`` as the
    preferred construction path and ``run()`` to start the stdio transport.
    """

    def __init__(
        self,
        *,
        config: MCPServerConfig | None = None,
        client_factory: ClientFactory | None = None,
        mcp_server: FastMCP | None = None,
    ) -> None:
        self._config = config or MCPServerConfig.from_env()
        self._client_factory = client_factory or _default_client_factory
        self._mcp = mcp_server or FastMCP("Cobo Agent Wallet")
        self._client_context: AsyncContextManager[WalletAPIClient] | None = None
        self._toolkit: AgentWalletToolkit | None = None
        self._tool_handlers: dict[str, Callable[..., Any]] | None = None
        self._client_lock = asyncio.Lock()
        self._register_tools()

    @property
    def mcp(self) -> FastMCP:
        """The underlying ``FastMCP`` instance."""
        return self._mcp

    async def get_tools(self) -> dict[str, Any]:
        """Return the tools registered with the underlying FastMCP instance.

        Handles both synchronous and awaitable return values from
        ``FastMCP.get_tools`` for compatibility across FastMCP versions.

        Returns:
            A dict mapping tool names to their FastMCP tool descriptors.
        """
        tools = self._mcp.get_tools()
        if hasattr(tools, "__await__"):
            return await tools
        return tools

    def run(self) -> None:
        """Start MCP server with stdio transport only."""

        self._mcp.run(transport="stdio")

    async def aclose(self) -> None:
        """Close the cached SDK client context, if initialized."""

        async with self._client_lock:
            if self._client_context is None:
                return
            await self._client_context.__aexit__(None, None, None)
            self._client_context = None
            self._toolkit = None
            self._tool_handlers = None

    def _resolve_api_key(self) -> str:
        """Return the API key from config or environment, raising if absent."""
        api_key = self._config.api_key or os.getenv(AGENT_WALLET_API_KEY)
        if not api_key:
            raise RuntimeError(
                f"Missing API key. Set {AGENT_WALLET_API_KEY} before starting the MCP stdio server."
            )
        return api_key

    async def _get_toolkit(self) -> AgentWalletToolkit:
        """Return the cached toolkit, initialising the SDK client on first call."""
        if self._toolkit is not None:
            return self._toolkit

        async with self._client_lock:
            if self._toolkit is None:
                api_key = self._resolve_api_key()
                client_context = self._client_factory(api_key, self._config)
                client = await client_context.__aenter__()
                self._client_context = client_context
                toolkit = AgentWalletToolkit(
                    client,
                    include_tools=list(self._config.include_tools)
                    if self._config.include_tools is not None
                    else None,
                    exclude_tools=list(self._config.exclude_tools),
                )
                self._toolkit = toolkit
                self._tool_handlers = {tool.name: tool.handler for tool in toolkit.get_tools()}

        assert self._toolkit is not None
        return self._toolkit

    async def _invoke_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Invoke a registered tool by name, translating SDK exceptions as needed.

        Policy denials are returned as normal tool content so MCP clients can
        inspect the denial payload and retry. Non-policy API failures are
        re-raised as ``RuntimeError`` so FastMCP surfaces them as protocol
        errors.

        Args:
            tool_name: Registered name of the tool to invoke.
            **kwargs: Keyword arguments forwarded to the tool handler.

        Returns:
            The raw return value from the tool handler.

        Raises:
            RuntimeError: If the tool raises a non-policy API error.
        """
        await self._get_toolkit()
        assert self._tool_handlers is not None
        handler = self._tool_handlers[tool_name]
        try:
            return await handler(**kwargs)
        except PolicyDeniedError as exc:
            denial = exc.denial
            return {
                "error": "POLICY_DENIED",
                "status_code": exc.status_code,
                "message": str(exc),
                "code": denial.code,
                "reason": denial.reason,
                "details": denial.details,
                "suggestion": denial.suggestion,
                "formatted": AgentWalletToolkit._format_denial(denial),
                "retryable": True,
            }
        except ApiException as exc:
            body: Any = exc.body
            if isinstance(exc.body, str):
                try:
                    body = json.loads(exc.body)
                except (json.JSONDecodeError, ValueError):
                    body = {"raw": exc.body}

            if exc.status == 403 and isinstance(body, dict):
                from cobo_agentic_wallet.errors import PolicyDenial

                denial = PolicyDenial.try_from_response(body)
                if denial:
                    return {
                        "error": "POLICY_DENIED",
                        "status_code": 403,
                        "message": denial.reason,
                        "code": denial.code,
                        "reason": denial.reason,
                        "details": denial.details,
                        "suggestion": denial.suggestion,
                        "formatted": AgentWalletToolkit._format_denial(denial),
                        "retryable": True,
                    }

            message = json.dumps(
                {
                    "error": "API_ERROR",
                    "status_code": exc.status or 500,
                    "message": str(exc.reason or exc),
                    "response": body,
                },
                sort_keys=True,
            )
            raise RuntimeError(message) from exc
        except APIError as exc:
            message = json.dumps(
                {
                    "error": "API_ERROR",
                    "status_code": exc.status_code,
                    "message": str(exc),
                    "response": exc.response_body,
                },
                sort_keys=True,
            )
            raise RuntimeError(message) from exc

    def _register_tools(self) -> None:
        """Register all tool specs from ``list_tool_specs`` with the FastMCP instance."""
        tool_specs = AgentWalletToolkit._select_tools(
            list_tool_specs(),
            include_tools=self._config.include_tools,
            exclude_tools=set(self._config.exclude_tools),
        )
        for tool_spec in tool_specs:
            wrapper = _build_tool_wrapper(
                tool_name=tool_spec.name,
                parameters_schema=tool_spec.parameters,
                invoke_tool=self._invoke_tool,
            )
            self._mcp.tool(
                wrapper,
                name=tool_spec.name,
                description=tool_spec.description,
            )


def create_server(
    *,
    config: MCPServerConfig | None = None,
    client_factory: ClientFactory | None = None,
    mcp_server: FastMCP | None = None,
) -> AgentWalletMCPServer:
    """Build and return an :class:`AgentWalletMCPServer` with the given config and factories."""

    return AgentWalletMCPServer(
        config=config,
        client_factory=client_factory,
        mcp_server=mcp_server,
    )


def run() -> None:
    """Entrypoint for ``python -m cobo_agentic_wallet.mcp``."""

    create_server().run()


__all__ = [
    "AGENT_WALLET_API_KEY",
    "AGENT_WALLET_EXCLUDE_TOOLS",
    "AGENT_WALLET_INCLUDE_TOOLS",
    "AGENT_WALLET_API_URL",
    "AGENT_WALLET_TIMEOUT",
    "AgentWalletMCPServer",
    "MCPServerConfig",
    "create_server",
    "run",
]

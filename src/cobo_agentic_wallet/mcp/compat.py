"""Compatibility shims for known FastMCP/MCP version skews."""

from __future__ import annotations

import importlib


def ensure_fastmcp_compat() -> None:
    """Patch MCP client naming drift expected by some FastMCP releases.

    Some FastMCP versions expect ``mcp.client.streamable_http.streamable_http_client``
    but older MCP packages only expose ``streamablehttp_client``.  This shim
    creates the expected alias on the already-imported module so callers do not
    need to guard against the difference themselves.
    """

    try:
        streamable_http = importlib.import_module("mcp.client.streamable_http")
    except ModuleNotFoundError:
        # Optional `mcp` package (pull in via `fastmcp` / `cobo-agentic-wallet[mcp]`).
        return
    if hasattr(streamable_http, "streamable_http_client"):
        return
    legacy = getattr(streamable_http, "streamablehttp_client", None)
    if legacy is not None:
        setattr(streamable_http, "streamable_http_client", legacy)

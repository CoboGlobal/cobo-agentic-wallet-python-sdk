"""Metadata operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class MetadataMixin:
    """Metadata operations mixin (auto-generated)."""

    _extract_result: Any
    _metadata_api: Any

    async def get_chain_info_by_chain_id(self: "BaseClient", chain_id: str) -> Any:
        """Get chain info"""
        response = await self._metadata_api.get_chain_info_by_chain_id(chain_id)
        return self._extract_result(response)

    async def list_assets(
        self: "BaseClient",
        wallet_type: Any | None = None,
        chain_ids: str | None = None,
        token_ids: str | None = None,
        limit: int | None = None,
        before: str | None = None,
        after: str | None = None,
    ) -> Any:
        """List supported assets"""
        response = await self._metadata_api.list_assets(
            wallet_type, chain_ids, token_ids, limit, before, after
        )
        return self._extract_result(response)

    async def list_chains(
        self: "BaseClient",
        wallet_type: Any | None = None,
        chain_ids: str | None = None,
        limit: int | None = None,
        before: str | None = None,
        after: str | None = None,
    ) -> Any:
        """List supported chains"""
        response = await self._metadata_api.list_chains(
            wallet_type, chain_ids, limit, before, after
        )
        return self._extract_result(response)

    async def search_tokens(self: "BaseClient", symbol: str) -> Any:
        """Search tokens by symbol"""
        response = await self._metadata_api.search_tokens(symbol)
        return self._extract_result(response)

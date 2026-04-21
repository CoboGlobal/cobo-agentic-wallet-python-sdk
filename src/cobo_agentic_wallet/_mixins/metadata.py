"""Metadata operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

from cobo_agentic_wallet_api.models.eth_call_request import EthCallRequest

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class MetadataMixin:
    """Metadata operations mixin (auto-generated)."""

    _extract_result: Any
    _metadata_api: Any

    async def eth_call(
        self: "BaseClient",
        chain_id: str = None,
        to: str = None,
        data: str = None,
        var_from: str | None = None,
        block: str | None = "latest",
    ) -> Any:
        """Call a view/pure function on an EVM contract"""
        eth_call_request = EthCallRequest(
            chain_id=chain_id, to=to, data=data, var_from=var_from, block=block
        )
        response = await self._metadata_api.eth_call(eth_call_request)
        return self._extract_result(response)

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

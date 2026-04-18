"""Wallet operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

from cobo_agentic_wallet_api.models.wallet_address_create import WalletAddressCreate
from cobo_agentic_wallet_api.models.wallet_create import WalletCreate
from cobo_agentic_wallet_api.models.wallet_reshare_request import WalletReshareRequest
from cobo_agentic_wallet_api.models.wallet_tss_callback_request import WalletTssCallbackRequest

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class WalletMixin:
    """Wallet operations mixin (auto-generated)."""

    _extract_result: Any
    _wallets_api: Any

    async def confirm_wallet_pair(self: "BaseClient", wallet_pair_confirm: Any) -> Any:
        """Confirm wallet pairing"""
        response = await self._wallets_api.confirm_wallet_pair(wallet_pair_confirm)
        return self._extract_result(response)

    async def create_wallet(
        self: "BaseClient",
        wallet_type: Any = None,
        name: str = None,
        group_type: Any | None = None,
        main_node_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        for_owner: bool | None = False,
    ) -> Any:
        """Create wallet"""
        wallet_create = WalletCreate(
            wallet_type=wallet_type,
            name=name,
            group_type=group_type,
            main_node_id=main_node_id,
            metadata=metadata,
            for_owner=for_owner,
        )
        response = await self._wallets_api.create_wallet(wallet_create)
        return self._extract_result(response)

    async def create_wallet_address(
        self: "BaseClient",
        wallet_uuid: str,
        *,
        chain_id: str | None = None,
        chain_type: str | None = None,
    ) -> Any:
        """Create wallet address"""
        wallet_address_create = WalletAddressCreate(chain_id=chain_id, chain_type=chain_type)
        response = await self._wallets_api.create_wallet_address(wallet_uuid, wallet_address_create)
        return self._extract_result(response)

    async def get_pair_info(self: "BaseClient", token: str) -> Any:
        """Get pair info by token"""
        response = await self._wallets_api.get_pair_info(token)
        return self._extract_result(response)

    async def get_pair_info_by_wallet(self: "BaseClient", wallet_uuid: str) -> Any:
        """Get pair info by wallet"""
        response = await self._wallets_api.get_pair_info_by_wallet(wallet_uuid)
        return self._extract_result(response)

    async def get_wallet(
        self: "BaseClient", wallet_uuid: str, include_spend_summary: bool | None = None
    ) -> Any:
        """Get wallet"""
        response = await self._wallets_api.get_wallet(wallet_uuid, include_spend_summary)
        return self._extract_result(response)

    async def get_wallet_node_status(self: "BaseClient", wallet_uuid: str) -> Any:
        """Get node status"""
        response = await self._wallets_api.get_wallet_node_status(wallet_uuid)
        return self._extract_result(response)

    async def initiate_wallet_pair(self: "BaseClient", wallet_pair_initiate: Any) -> Any:
        """Initiate wallet pairing"""
        response = await self._wallets_api.initiate_wallet_pair(wallet_pair_initiate)
        return self._extract_result(response)

    async def list_wallet_addresses(self: "BaseClient", wallet_uuid: str) -> Any:
        """List wallet addresses"""
        response = await self._wallets_api.list_wallet_addresses(wallet_uuid)
        return self._extract_result(response)

    async def list_wallets(
        self: "BaseClient",
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        include_archived: bool | None = None,
        main_node_id: str | None = None,
    ) -> Any:
        """List all wallets"""
        response = await self._wallets_api.list_wallets(
            after, before, offset, limit, include_archived, main_node_id
        )
        return self._extract_result(response)

    async def update_wallet(self: "BaseClient", wallet_uuid: str, wallet_update: Any) -> Any:
        """Update wallet"""
        response = await self._wallets_api.update_wallet(wallet_uuid, wallet_update)
        return self._extract_result(response)

    async def wallet_reshare(self: "BaseClient", wallet_uuid: str, *, node_id: str = None) -> Any:
        """Initiate wallet reshare"""
        wallet_reshare_request = WalletReshareRequest(node_id=node_id)
        response = await self._wallets_api.wallet_reshare(wallet_uuid, wallet_reshare_request)
        return self._extract_result(response)

    async def wallet_tss_callback(
        self: "BaseClient",
        wallet_uuid: str,
        *,
        tss_request_id: str = None,
        status: int = None,
        results: list[Any] | None = None,
        failed_reasons: list[str] | None = None,
    ) -> Any:
        """Report TSS request callback"""
        wallet_tss_callback_request = WalletTssCallbackRequest(
            tss_request_id=tss_request_id,
            status=status,
            results=results,
            failed_reasons=failed_reasons,
        )
        response = await self._wallets_api.wallet_tss_callback(
            wallet_uuid, wallet_tss_callback_request
        )
        return self._extract_result(response)

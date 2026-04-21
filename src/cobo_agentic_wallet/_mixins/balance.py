"""Balance operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class BalanceMixin:
    """Balance operations mixin (auto-generated)."""

    _extract_result: Any
    _balance_api: Any

    async def list_balances(
        self: "BaseClient",
        wallet_uuid: str | None = None,
        chain_id: str | None = None,
        address: str | None = None,
        token_id: str | None = None,
        force_refresh: bool | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
    ) -> Any:
        """List token balances"""
        response = await self._balance_api.list_balances(
            wallet_uuid, chain_id, address, token_id, force_refresh, limit, after, before, offset
        )
        return self._extract_result(response)

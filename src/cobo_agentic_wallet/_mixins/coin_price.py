"""Coinprice operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class CoinPriceMixin:
    """Coinprice operations mixin (auto-generated)."""

    _extract_result: Any
    _coin_price_api: Any

    async def get_asset_coin_prices(
        self: "BaseClient", asset_coins: str, currency: str | None = None
    ) -> Any:
        """Get coin prices"""
        response = await self._coin_price_api.get_asset_coin_prices(asset_coins, currency)
        return self._extract_result(response)

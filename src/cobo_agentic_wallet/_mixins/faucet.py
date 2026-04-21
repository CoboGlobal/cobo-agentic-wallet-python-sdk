"""Faucet operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

from cobo_agentic_wallet_api.models.faucet_deposit_request import FaucetDepositRequest

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class FaucetMixin:
    """Faucet operations mixin (auto-generated)."""

    _extract_result: Any
    _faucet_api: Any

    async def deposit(self: "BaseClient", address: str = None, token_id: str = None) -> Any:
        """Request faucet deposit"""
        faucet_deposit_request = FaucetDepositRequest(address=address, token_id=token_id)
        response = await self._faucet_api.deposit(faucet_deposit_request)
        return self._extract_result(response)

    async def list_tokens(self: "BaseClient") -> Any:
        """List faucet tokens"""
        response = await self._faucet_api.list_tokens()
        return self._extract_result(response)

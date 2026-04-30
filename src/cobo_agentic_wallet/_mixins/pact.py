"""Pact operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

from cobo_agentic_wallet_api.models.pact_submit_request import PactSubmitRequest
from cobo_agentic_wallet_api.models.pact_update_completion_conditions_request import (
    PactUpdateCompletionConditionsRequest,
)
from cobo_agentic_wallet_api.models.pact_update_policies_request import PactUpdatePoliciesRequest

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class PactMixin:
    """Pact operations mixin (auto-generated)."""

    _extract_result: Any
    _pacts_api: Any

    async def get_pact(self: "BaseClient", pact_id: str) -> Any:
        """Get pact detail"""
        response = await self._pacts_api.get_pact(pact_id)
        return self._extract_result(response)

    async def get_wallet_pact_history(
        self: "BaseClient",
        wallet_id: str,
        range: str,
        metric: Any | None = None,
        lang: Any | None = None,
    ) -> Any:
        """Get wallet pact history"""
        response = await self._pacts_api.get_wallet_pact_history(wallet_id, range, metric, lang)
        return self._extract_result(response)

    async def get_wallet_pact_stats(
        self: "BaseClient",
        wallet_id: str,
        include_default: bool | None = None,
        lang: Any | None = None,
    ) -> Any:
        """Get wallet pact statistics"""
        response = await self._pacts_api.get_wallet_pact_stats(wallet_id, include_default, lang)
        return self._extract_result(response)

    async def list_pact_events(
        self: "BaseClient",
        pact_id: str,
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """List pact events"""
        response = await self._pacts_api.list_pact_events(pact_id, after, before, offset, limit)
        return self._extract_result(response)

    async def list_pacts(
        self: "BaseClient",
        status: Any | None = None,
        wallet_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        include_default: bool | None = None,
    ) -> Any:
        """List pacts"""
        response = await self._pacts_api.list_pacts(
            status, wallet_id, after, before, offset, limit, include_default
        )
        return self._extract_result(response)

    async def revoke_pact(self: "BaseClient", pact_id: str) -> Any:
        """Revoke active pact"""
        response = await self._pacts_api.revoke_pact(pact_id)
        return self._extract_result(response)

    async def submit_pact(
        self: "BaseClient",
        wallet_id: str = None,
        intent: str = None,
        original_intent: str | None = None,
        spec: Any = None,
        name: str | None = None,
        recipe_slugs: list[str] | None = None,
    ) -> Any:
        """Submit pact for approval"""
        pact_submit_request = PactSubmitRequest(
            wallet_id=wallet_id,
            intent=intent,
            original_intent=original_intent,
            spec=spec,
            name=name,
            recipe_slugs=recipe_slugs,
        )
        response = await self._pacts_api.submit_pact(pact_submit_request)
        return self._extract_result(response)

    async def update_completion_conditions(
        self: "BaseClient", pact_id: str, *, completion_conditions: list[Any] = None
    ) -> Any:
        """Update completion conditions"""
        pact_update_completion_conditions_request = PactUpdateCompletionConditionsRequest(
            completion_conditions=completion_conditions
        )
        response = await self._pacts_api.update_completion_conditions(
            pact_id, pact_update_completion_conditions_request
        )
        return self._extract_result(response)

    async def update_policies(
        self: "BaseClient", pact_id: str, *, policies: list[Any] = None
    ) -> Any:
        """Update pact policies"""
        pact_update_policies_request = PactUpdatePoliciesRequest(policies=policies)
        response = await self._pacts_api.update_policies(pact_id, pact_update_policies_request)
        return self._extract_result(response)

    async def withdraw_pact(self: "BaseClient", pact_id: str) -> Any:
        """Withdraw pending pact"""
        response = await self._pacts_api.withdraw_pact(pact_id)
        return self._extract_result(response)

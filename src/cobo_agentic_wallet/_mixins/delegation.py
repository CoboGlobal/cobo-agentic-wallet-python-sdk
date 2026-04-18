"""Delegation operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from datetime import datetime

from cobo_agentic_wallet_api.models.delegation_create import DelegationCreate
from cobo_agentic_wallet_api.models.delegation_freeze_request import DelegationFreezeRequest

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class DelegationMixin:
    """Delegation operations mixin (auto-generated)."""

    _extract_result: Any
    _delegations_api: Any

    async def create_delegation(
        self: "BaseClient",
        operator_id: str = None,
        wallet_id: str = None,
        permissions: list[Any] = None,
        policies: list[Any] | None = None,
        expires_at: datetime | None = None,
    ) -> Any:
        """Create delegation"""
        delegation_create = DelegationCreate(
            operator_id=operator_id,
            wallet_id=wallet_id,
            permissions=permissions,
            policies=policies,
            expires_at=expires_at,
        )
        response = await self._delegations_api.create_delegation(delegation_create)
        return self._extract_result(response)

    async def freeze_delegations(
        self: "BaseClient",
        scope: Any = None,
        owner_id: str | None = None,
        wallet_id: str | None = None,
        delegation_id: str | None = None,
        reason: str | None = None,
    ) -> Any:
        """Freeze delegations"""
        delegation_freeze_request = DelegationFreezeRequest(
            scope=scope,
            owner_id=owner_id,
            wallet_id=wallet_id,
            delegation_id=delegation_id,
            reason=reason,
        )
        response = await self._delegations_api.freeze_delegations(delegation_freeze_request)
        return self._extract_result(response)

    async def get_delegation(self: "BaseClient", delegation_id: str) -> Any:
        """Get delegation"""
        response = await self._delegations_api.get_delegation(delegation_id)
        return self._extract_result(response)

    async def list_delegations(
        self: "BaseClient",
        operator_id: str | None = None,
        wallet_id: str | None = None,
        status: Any | None = None,
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """List delegations"""
        response = await self._delegations_api.list_delegations(
            operator_id, wallet_id, status, after, before, offset, limit
        )
        return self._extract_result(response)

    async def list_received_delegations(
        self: "BaseClient",
        owner_id: str | None = None,
        wallet_id: str | None = None,
        status: Any | None = None,
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """List received delegations"""
        response = await self._delegations_api.list_received_delegations(
            owner_id, wallet_id, status, after, before, offset, limit
        )
        return self._extract_result(response)

    async def revoke_delegation(self: "BaseClient", delegation_id: str) -> Any:
        """Revoke delegation"""
        response = await self._delegations_api.revoke_delegation(delegation_id)
        return self._extract_result(response)

    async def unfreeze_delegations(
        self: "BaseClient",
        scope: Any = None,
        owner_id: str | None = None,
        wallet_id: str | None = None,
        delegation_id: str | None = None,
        reason: str | None = None,
    ) -> Any:
        """Unfreeze delegations"""
        delegation_freeze_request = DelegationFreezeRequest(
            scope=scope,
            owner_id=owner_id,
            wallet_id=wallet_id,
            delegation_id=delegation_id,
            reason=reason,
        )
        response = await self._delegations_api.unfreeze_delegations(delegation_freeze_request)
        return self._extract_result(response)

    async def update_delegation(
        self: "BaseClient", delegation_id: str, delegation_update: Any
    ) -> Any:
        """Update delegation"""
        response = await self._delegations_api.update_delegation(delegation_id, delegation_update)
        return self._extract_result(response)

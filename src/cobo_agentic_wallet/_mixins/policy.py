"""Policy operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from cobo_agentic_wallet_api.models.policy_create import PolicyCreate
from cobo_agentic_wallet_api.models.policy_dry_run_request import PolicyDryRunRequest
from cobo_agentic_wallet_api.models.reject_pending_operation_request import (
    RejectPendingOperationRequest,
)

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class PolicyMixin:
    """Policy operations mixin (auto-generated)."""

    _extract_result: Any
    _policies_api: Any

    async def approve_pending_operation(self: "BaseClient", pending_operation_id: str) -> Any:
        """Approve pending operation"""
        response = await self._policies_api.approve_pending_operation(pending_operation_id)
        return self._extract_result(response)

    async def create_policy(
        self: "BaseClient",
        scope: Any,
        name: str,
        policy_type: Any,
        rules: dict[str, Any],
        wallet_id: str | None = None,
        delegation_id: str | None = None,
        priority: int | None = 0,
        is_active: bool | None = True,
    ) -> Any:
        """Create policy"""
        policy_create = PolicyCreate(
            scope=scope,
            wallet_id=wallet_id,
            delegation_id=delegation_id,
            name=name,
            policy_type=policy_type,
            rules=rules,
            priority=priority,
            is_active=is_active,
        )
        response = await self._policies_api.create_policy(policy_create)
        return self._extract_result(response)

    async def deactivate_policy(self: "BaseClient", policy_id: str) -> Any:
        """Deactivate policy"""
        response = await self._policies_api.deactivate_policy(policy_id)
        return self._extract_result(response)

    async def dry_run_policy(
        self: "BaseClient",
        wallet_id: str,
        operation_type: Any,
        amount: str,
        chain_id: str,
        delegation_id: str | None = None,
        token_id: str | None = None,
        dst_addr: str | None = None,
        contract_addr: str | None = None,
        calldata: str | None = None,
        instructions: list[dict[str, Any] | None] | None = None,
        principal_id: str | None = None,
    ) -> Any:
        """Dry-run policy"""
        policy_dry_run_request = PolicyDryRunRequest(
            wallet_id=wallet_id,
            delegation_id=delegation_id,
            operation_type=operation_type,
            amount=amount,
            chain_id=chain_id,
            token_id=token_id,
            dst_addr=dst_addr,
            contract_addr=contract_addr,
            calldata=calldata,
            instructions=instructions,
            principal_id=principal_id,
        )
        response = await self._policies_api.dry_run_policy(policy_dry_run_request)
        return self._extract_result(response)

    async def get_pending_operation(self: "BaseClient", pending_operation_id: str) -> Any:
        """Get pending operation"""
        response = await self._policies_api.get_pending_operation(pending_operation_id)
        return self._extract_result(response)

    async def get_policy(self: "BaseClient", policy_id: str) -> Any:
        """Get policy"""
        response = await self._policies_api.get_policy(policy_id)
        return self._extract_result(response)

    async def list_pending_operations(
        self: "BaseClient",
        status: Any | None = None,
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """List pending operations"""
        response = await self._policies_api.list_pending_operations(
            status, after, before, offset, limit
        )
        return self._extract_result(response)

    async def list_policies(
        self: "BaseClient",
        scope: Any | None = None,
        wallet_id: str | None = None,
        delegation_id: str | None = None,
        policy_type: Any | None = None,
        include_inactive: bool | None = None,
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """List all policies"""
        response = await self._policies_api.list_policies(
            scope,
            wallet_id,
            delegation_id,
            policy_type,
            include_inactive,
            after,
            before,
            offset,
            limit,
        )
        return self._extract_result(response)

    async def reject_pending_operation(
        self: "BaseClient", pending_operation_id: str, *, reason: str | None = None
    ) -> Any:
        """Reject pending operation"""
        reject_pending_operation_request = RejectPendingOperationRequest(reason=reason)
        response = await self._policies_api.reject_pending_operation(
            pending_operation_id, reject_pending_operation_request
        )
        return self._extract_result(response)

    async def update_policy(self: "BaseClient", policy_id: str, policy_update: Any) -> Any:
        """Update policy"""
        response = await self._policies_api.update_policy(policy_id, policy_update)
        return self._extract_result(response)

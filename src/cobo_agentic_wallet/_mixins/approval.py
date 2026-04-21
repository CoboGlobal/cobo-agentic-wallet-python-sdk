"""Approval operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from cobo_agentic_wallet_api.models.resolve_approval_v2_request import ResolveApprovalV2Request

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class ApprovalMixin:
    """Approval operations mixin (auto-generated)."""

    _extract_result: Any
    _approvals_api: Any

    async def get_approval(self: "BaseClient", approval_id: str) -> Any:
        """Get approval details"""
        response = await self._approvals_api.get_approval(approval_id)
        return self._extract_result(response)

    async def list_approvals(
        self: "BaseClient",
        subject_type: Any | None = None,
        status: Any | None = None,
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """List approvals"""
        response = await self._approvals_api.list_approvals(
            subject_type, status, after, before, offset, limit
        )
        return self._extract_result(response)

    async def resolve_approval(
        self: "BaseClient", approval_id: str, *, action: Any, response: Any | None = None
    ) -> Any:
        """Resolve approval request"""
        resolve_approval_v2_request = ResolveApprovalV2Request(action=action, response=response)
        response = await self._approvals_api.resolve_approval(
            approval_id, resolve_approval_v2_request
        )
        return self._extract_result(response)

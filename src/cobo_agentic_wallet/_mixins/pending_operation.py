"""Pendingoperation operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

from cobo_agentic_wallet_api.models.reject_pending_operation_request import (
    RejectPendingOperationRequest,
)

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class PendingOperationMixin:
    """Pendingoperation operations mixin (auto-generated)."""

    _extract_result: Any
    _pending_operations_api: Any

    async def approve_pending_operation(self: "BaseClient", pending_operation_id: str) -> Any:
        """Approve pending operation"""
        response = await self._pending_operations_api.approve_pending_operation(
            pending_operation_id
        )
        return self._extract_result(response)

    async def get_pending_operation(self: "BaseClient", pending_operation_id: str) -> Any:
        """Get pending operation"""
        response = await self._pending_operations_api.get_pending_operation(pending_operation_id)
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
        response = await self._pending_operations_api.list_pending_operations(
            status, after, before, offset, limit
        )
        return self._extract_result(response)

    async def reject_pending_operation(
        self: "BaseClient", pending_operation_id: str, *, reason: str | None = None
    ) -> Any:
        """Reject pending operation"""
        reject_pending_operation_request = RejectPendingOperationRequest(reason=reason)
        response = await self._pending_operations_api.reject_pending_operation(
            pending_operation_id, reject_pending_operation_request
        )
        return self._extract_result(response)

"""Audit operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class AuditMixin:
    """Audit operations mixin (auto-generated)."""

    _extract_result: Any
    _audit_api: Any

    async def list_audit_logs(
        self: "BaseClient",
        wallet_id: str | None = None,
        principal_id: str | None = None,
        action: str | None = None,
        result: Any | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        after: str | None = None,
        before: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> Any:
        """List audit logs"""
        response = await self._audit_api.list_audit_logs(
            wallet_id,
            principal_id,
            action,
            result,
            start_time,
            end_time,
            after,
            before,
            cursor,
            limit,
        )
        return self._extract_result(response)

"""Health operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class HealthMixin:
    """Health operations mixin (auto-generated)."""

    _extract_result: Any
    _health_api: Any

    async def health_check(self: "BaseClient") -> Any:
        """Health Check"""
        response = await self._health_api.health_check()
        return self._extract_result(response)

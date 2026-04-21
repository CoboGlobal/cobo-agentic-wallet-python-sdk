"""Ap2 operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class AP2Mixin:
    """AP2 merchant operations mixin (auto-generated)."""

    _extract_result: Any
    _ap2_api: Any

    async def get_merchants(self: "BaseClient") -> Any:
        """List AP2 merchants"""
        response = await self._ap2_api.get_merchants()
        return self._extract_result(response)

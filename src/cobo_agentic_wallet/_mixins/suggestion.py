"""Suggestion operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class SuggestionMixin:
    """Suggestion operations mixin (auto-generated)."""

    _extract_result: Any
    _suggestions_api: Any

    async def get_suggestion(self: "BaseClient", key: Any) -> Any:
        """Get suggestion by key"""
        response = await self._suggestions_api.get_suggestion(key)
        return self._extract_result(response)

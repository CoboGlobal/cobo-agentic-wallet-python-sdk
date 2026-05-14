"""Recipe operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

from cobo_agentic_wallet_api.models.search_recipes_request import SearchRecipesRequest

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class RecipeMixin:
    """Recipe operations mixin (auto-generated)."""

    _extract_result: Any
    _recipes_api: Any

    async def search_recipes(
        self: "BaseClient",
        query: str | None = "",
        source: Any | None = None,
        limit: int | None = 1,
        chain: str | None = None,
        token: str | None = None,
        keywords: list[str] | None = None,
        search_type: Any | None = None,
        wallet_id: str | None = None,
    ) -> Any:
        """Search recipes"""
        search_recipes_request = SearchRecipesRequest(
            query=query,
            source=source,
            limit=limit,
            chain=chain,
            token=token,
            keywords=keywords,
            search_type=search_type,
            wallet_id=wallet_id,
        )
        response = await self._recipes_api.search_recipes(search_recipes_request)
        return self._extract_result(response)

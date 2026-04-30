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

    async def list_pact_templates(
        self: "BaseClient",
        offset: int | None = None,
        limit: int | None = None,
        recipe_slug: str | None = None,
    ) -> Any:
        """List pact templates"""
        response = await self._recipes_api.list_pact_templates(offset, limit, recipe_slug)
        return self._extract_result(response)

    async def search_recipes(
        self: "BaseClient",
        query: str | None = "",
        source: Any | None = None,
        limit: int | None = 1,
        chain: str | None = None,
        token: str | None = None,
        keywords: list[str] | None = None,
        search_type: Any | None = None,
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
        )
        response = await self._recipes_api.search_recipes(search_recipes_request)
        return self._extract_result(response)

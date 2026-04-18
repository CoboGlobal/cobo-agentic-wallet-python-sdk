"""Recipe operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

from cobo_agentic_wallet_api.models.recipe_create import RecipeCreate
from cobo_agentic_wallet_api.models.recipe_review_request import RecipeReviewRequest
from cobo_agentic_wallet_api.models.recipe_submission_create import RecipeSubmissionCreate
from cobo_agentic_wallet_api.models.search_recipes_request import SearchRecipesRequest

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class RecipeMixin:
    """Recipe operations mixin (auto-generated)."""

    _extract_result: Any
    _recipes_api: Any

    async def archive_recipe(self: "BaseClient", recipe_id: str) -> Any:
        """Archive recipe"""
        response = await self._recipes_api.archive_recipe(recipe_id)
        return self._extract_result(response)

    async def create_recipe(
        self: "BaseClient",
        slug: str,
        title: str,
        description: str,
        content_markdown: str | None = "",
        chains: list[str] | None = None,
        tokens: dict[str, dict[str, str]] | None = None,
        tags: list[str] | None = None,
        category: list[str] | None = None,
        example_prompts: list[str] | None = None,
        icon: str | None = "📋",
        author_name: str | None = None,
        sdk_example_path: str | None = None,
        locale: str | None = "en",
        featured: bool | None = False,
        verified: bool | None = False,
        auto_publish: bool | None = False,
    ) -> Any:
        """Create recipe"""
        recipe_create = RecipeCreate(
            slug=slug,
            title=title,
            description=description,
            content_markdown=content_markdown,
            chains=chains,
            tokens=tokens,
            tags=tags,
            category=category,
            example_prompts=example_prompts,
            icon=icon,
            author_name=author_name,
            sdk_example_path=sdk_example_path,
            locale=locale,
            featured=featured,
            verified=verified,
            auto_publish=auto_publish,
        )
        response = await self._recipes_api.create_recipe(recipe_create)
        return self._extract_result(response)

    async def get_recipe_by_slug(
        self: "BaseClient", slug: str, track_view: bool | None = None
    ) -> Any:
        """Get recipe detail by slug"""
        response = await self._recipes_api.get_recipe_by_slug(slug, track_view)
        return self._extract_result(response)

    async def get_recipe_document(
        self: "BaseClient", document_id: str, source: Any | None = None
    ) -> Any:
        """Get full recipe document by ID"""
        response = await self._recipes_api.get_recipe_document(document_id, source)
        return self._extract_result(response)

    async def get_recipe_search_count(self: "BaseClient", recipe_id: str) -> Any:
        """Get recipe search count"""
        response = await self._recipes_api.get_recipe_search_count(recipe_id)
        return self._extract_result(response)

    async def list_featured_recipes(self: "BaseClient", limit: int | None = None) -> Any:
        """List featured recipes"""
        response = await self._recipes_api.list_featured_recipes(limit)
        return self._extract_result(response)

    async def list_recipe_categories(self: "BaseClient") -> Any:
        """List recipe categories"""
        response = await self._recipes_api.list_recipe_categories()
        return self._extract_result(response)

    async def list_recipe_library(
        self: "BaseClient",
        offset: int | None = None,
        limit: int | None = None,
        category: str | None = None,
        tag: str | None = None,
        chain: str | None = None,
        featured: bool | None = None,
        query: str | None = None,
        sort_by: Any | None = None,
    ) -> Any:
        """List recipes in the public library"""
        response = await self._recipes_api.list_recipe_library(
            offset, limit, category, tag, chain, featured, query, sort_by
        )
        return self._extract_result(response)

    async def review_recipe_submission(self: "BaseClient", recipe_id: str, *, action: Any) -> Any:
        """Review submitted recipe"""
        recipe_review_request = RecipeReviewRequest(action=action)
        response = await self._recipes_api.review_recipe_submission(
            recipe_id, recipe_review_request
        )
        return self._extract_result(response)

    async def search_recipes(
        self: "BaseClient",
        query: str,
        source: Any | None = None,
        mode: str | None = None,
        top_k: int | None = None,
        chunk_top_k: int | None = None,
        max_entity_tokens: int | None = None,
        max_relation_tokens: int | None = None,
        max_total_tokens: int | None = None,
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
            mode=mode,
            top_k=top_k,
            chunk_top_k=chunk_top_k,
            max_entity_tokens=max_entity_tokens,
            max_relation_tokens=max_relation_tokens,
            max_total_tokens=max_total_tokens,
            limit=limit,
            chain=chain,
            token=token,
            keywords=keywords,
            search_type=search_type,
        )
        response = await self._recipes_api.search_recipes(search_recipes_request)
        return self._extract_result(response)

    async def submit_recipe(
        self: "BaseClient",
        slug: str,
        title: str,
        description: str,
        content_markdown: str | None = "",
        chains: list[str] | None = None,
        tokens: dict[str, dict[str, str]] | None = None,
        tags: list[str] | None = None,
        category: list[str] | None = None,
        example_prompts: list[str] | None = None,
        icon: str | None = "📋",
        author_name: str | None = None,
        sdk_example_path: str | None = None,
        locale: str | None = "en",
    ) -> Any:
        """Submit community recipe"""
        recipe_submission_create = RecipeSubmissionCreate(
            slug=slug,
            title=title,
            description=description,
            content_markdown=content_markdown,
            chains=chains,
            tokens=tokens,
            tags=tags,
            category=category,
            example_prompts=example_prompts,
            icon=icon,
            author_name=author_name,
            sdk_example_path=sdk_example_path,
            locale=locale,
        )
        response = await self._recipes_api.submit_recipe(recipe_submission_create)
        return self._extract_result(response)

    async def track_recipe_share(self: "BaseClient", recipe_id: str) -> Any:
        """Increment recipe share count"""
        response = await self._recipes_api.track_recipe_share(recipe_id)
        return self._extract_result(response)

    async def track_recipe_use(self: "BaseClient", recipe_id: str) -> Any:
        """Increment recipe use count"""
        response = await self._recipes_api.track_recipe_use(recipe_id)
        return self._extract_result(response)

    async def update_recipe(self: "BaseClient", recipe_id: str, recipe_update: Any) -> Any:
        """Update recipe"""
        response = await self._recipes_api.update_recipe(recipe_id, recipe_update)
        return self._extract_result(response)

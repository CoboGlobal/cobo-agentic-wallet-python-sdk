"""Identity operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING
from datetime import datetime

from cobo_agentic_wallet_api.models.api_key_create import ApiKeyCreate
from cobo_agentic_wallet_api.models.principal_create import PrincipalCreate
from cobo_agentic_wallet_api.models.provision_request import ProvisionRequest

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class IdentityMixin:
    """Identity operations mixin (auto-generated)."""

    _extract_result: Any
    _identity_api: Any

    async def create_api_key(
        self: "BaseClient",
        principal_id: str | None = None,
        name: str = None,
        scopes: list[str] | None = None,
        expires_at: datetime | None = None,
    ) -> Any:
        """Create API key"""
        api_key_create = ApiKeyCreate(
            principal_id=principal_id, name=name, scopes=scopes, expires_at=expires_at
        )
        response = await self._identity_api.create_api_key(api_key_create)
        return self._extract_result(response)

    async def create_principal(
        self: "BaseClient",
        external_id: str = None,
        principal_type: Any = None,
        name: str = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """Create principal"""
        principal_create = PrincipalCreate(
            external_id=external_id, type=principal_type, name=name, metadata=metadata
        )
        response = await self._identity_api.create_principal(principal_create)
        return self._extract_result(response)

    async def get_agent_status(self: "BaseClient", agent_id: str) -> Any:
        """Get agent status"""
        response = await self._identity_api.get_agent_status(agent_id)
        return self._extract_result(response)

    async def list_api_keys(
        self: "BaseClient",
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """List API keys"""
        response = await self._identity_api.list_api_keys(after, before, offset, limit)
        return self._extract_result(response)

    async def list_my_agents(
        self: "BaseClient",
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """List my agents"""
        response = await self._identity_api.list_my_agents(after, before, offset, limit)
        return self._extract_result(response)

    async def list_principals(
        self: "BaseClient",
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        principal_type: Any | None = None,
    ) -> Any:
        """List all principals"""
        response = await self._identity_api.list_principals(
            after, before, offset, limit, principal_type
        )
        return self._extract_result(response)

    async def provision_agent(
        self: "BaseClient",
        token: str | None = None,
        invitation_code: str | None = None,
        name: str | None = None,
    ) -> Any:
        """Provision agent"""
        provision_request = ProvisionRequest(
            token=token, invitation_code=invitation_code, name=name
        )
        response = await self._identity_api.provision_agent(provision_request)
        return self._extract_result(response)

    async def revoke_api_key(self: "BaseClient", api_key_id: str) -> Any:
        """Revoke API key"""
        response = await self._identity_api.revoke_api_key(api_key_id)
        return self._extract_result(response)

    async def update_principal(self: "BaseClient", principal_id: str, principal_update: Any) -> Any:
        """Update principal"""
        response = await self._identity_api.update_principal(principal_id, principal_update)
        return self._extract_result(response)

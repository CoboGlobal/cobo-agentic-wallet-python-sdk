"""Base client with shared functionality for all mixins."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from cobo_agentic_wallet_api.api_client_async import AsyncApiClient
    from cobo_agentic_wallet_api.api.wallets_api_async import AsyncWalletsApi
    from cobo_agentic_wallet_api.api.transactions_api_async import AsyncTransactionsApi
    from cobo_agentic_wallet_api.api.transaction_records_api_async import AsyncTransactionRecordsApi
    from cobo_agentic_wallet_api.api.delegations_api_async import AsyncDelegationsApi
    from cobo_agentic_wallet_api.api.audit_api_async import AsyncAuditApi
    from cobo_agentic_wallet_api.api.identity_api_async import AsyncIdentityApi
    from cobo_agentic_wallet_api.api.health_api_async import AsyncHealthApi
    from cobo_agentic_wallet_api.api.meta_api_async import AsyncMetaApi
    from cobo_agentic_wallet_api.api.policies_api_async import AsyncPoliciesApi
    from cobo_agentic_wallet_api.api.coin_price_api_async import AsyncCoinPriceApi
    from cobo_agentic_wallet_api.api.metadata_api_async import AsyncMetadataApi
    from cobo_agentic_wallet_api.api.faucet_api_async import AsyncFaucetApi


class BaseClient:
    """Shared base for all Cobo Agentic Wallet mixin classes.

    Provides the ``_extract_result`` utility for unwrapping ``StandardResponse``
    envelopes, async context-manager support, and basic health-check helpers
    consumed by every domain mixin.
    """

    # Type hints for API objects (set by __init__ in WalletAPIClient)
    _api_client: "AsyncApiClient"
    _wallets_api: "AsyncWalletsApi"
    _transactions_api: "AsyncTransactionsApi"
    _transaction_records_api: "AsyncTransactionRecordsApi"
    _delegations_api: "AsyncDelegationsApi"
    _audit_api: "AsyncAuditApi"
    _identity_api: "AsyncIdentityApi"
    _health_api: "AsyncHealthApi"
    _meta_api: "AsyncMetaApi"
    _policies_api: "AsyncPoliciesApi"
    _coin_price_api: "AsyncCoinPriceApi"
    _metadata_api: "AsyncMetadataApi"
    _faucet_api: "AsyncFaucetApi"
    _service_auth_key: str | None

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._api_client.close()

    async def __aenter__(self) -> "BaseClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    @staticmethod
    def _extract_result(response: Any) -> Any:
        """Extract result from StandardResponse wrapper."""
        import json as json_module

        if response is None:
            return None
        if isinstance(response, dict):
            return response.get("result", response)
        if hasattr(response, "result"):
            result = response.result
            if result is not None:
                if isinstance(result, list):
                    return [
                        json_module.loads(item.model_dump_json())
                        if hasattr(item, "model_dump_json")
                        else item
                        for item in result
                    ]
                elif hasattr(result, "model_dump_json"):
                    return json_module.loads(result.model_dump_json())
            return result
        return response

    # ------------------------------------------------------------------
    # Health operations
    # ------------------------------------------------------------------

    async def ping(self) -> Any:
        """Health check - ping the API."""
        response = await self._meta_api.ping()
        return self._extract_result(response)

    async def health_check(self) -> Any:
        """Health check - get detailed health status."""
        response = await self._health_api.health_check()
        return self._extract_result(response)

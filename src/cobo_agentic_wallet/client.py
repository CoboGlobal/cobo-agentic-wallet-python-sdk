"""SDK client wrapper for the Cobo Agentic Wallet API."""

# Generated SDK imports
from cobo_agentic_wallet_api.configuration import Configuration
from cobo_agentic_wallet_api.api_client_async import AsyncApiClient
from cobo_agentic_wallet_api.api.wallets_api_async import AsyncWalletsApi
from cobo_agentic_wallet_api.api.transactions_api_async import AsyncTransactionsApi
from cobo_agentic_wallet_api.api.transaction_records_api_async import AsyncTransactionRecordsApi
from cobo_agentic_wallet_api.api.audit_api_async import AsyncAuditApi
from cobo_agentic_wallet_api.api.identity_api_async import AsyncIdentityApi
from cobo_agentic_wallet_api.api.health_api_async import AsyncHealthApi
from cobo_agentic_wallet_api.api.meta_api_async import AsyncMetaApi
from cobo_agentic_wallet_api.api.pending_operations_api_async import AsyncPendingOperationsApi
from cobo_agentic_wallet_api.api.coin_price_api_async import AsyncCoinPriceApi
from cobo_agentic_wallet_api.api.metadata_api_async import AsyncMetadataApi
from cobo_agentic_wallet_api.api.faucet_api_async import AsyncFaucetApi
from cobo_agentic_wallet_api.api.balance_api_async import AsyncBalanceApi
from cobo_agentic_wallet_api.api.pacts_api_async import AsyncPactsApi
from cobo_agentic_wallet_api.api.recipes_api_async import AsyncRecipesApi
from cobo_agentic_wallet_api.api.suggestions_api_async import AsyncSuggestionsApi
from cobo_agentic_wallet_api.api.telemetry_api_async import AsyncTelemetryApi

# Mixin imports
from cobo_agentic_wallet._mixins.base import BaseClient
from cobo_agentic_wallet._mixins.balance import BalanceMixin
from cobo_agentic_wallet._mixins.wallet import WalletMixin
from cobo_agentic_wallet._mixins.faucet import FaucetMixin
from cobo_agentic_wallet._mixins.transaction import TransactionMixin
from cobo_agentic_wallet._mixins.transaction_record import TransactionRecordMixin
from cobo_agentic_wallet._mixins.pending_operation import PendingOperationMixin
from cobo_agentic_wallet._mixins.identity import IdentityMixin
from cobo_agentic_wallet._mixins.audit import AuditMixin
from cobo_agentic_wallet._mixins.coin_price import CoinPriceMixin
from cobo_agentic_wallet._mixins.health import HealthMixin
from cobo_agentic_wallet._mixins.metadata import MetadataMixin
from cobo_agentic_wallet._mixins.pact import PactMixin
from cobo_agentic_wallet._mixins.recipe import RecipeMixin
from cobo_agentic_wallet._mixins.suggestion import SuggestionMixin
from cobo_agentic_wallet._mixins.telemetry import TelemetryMixin


class WalletAPIClient(
    BalanceMixin,
    WalletMixin,
    FaucetMixin,
    TransactionMixin,
    TransactionRecordMixin,
    PendingOperationMixin,
    IdentityMixin,
    AuditMixin,
    CoinPriceMixin,
    HealthMixin,
    MetadataMixin,
    PactMixin,
    RecipeMixin,
    SuggestionMixin,
    TelemetryMixin,
    BaseClient,
):
    """Async client for the Cobo Agentic Wallet API.

    Composes domain-specific mixins into a single entry point for all wallet,
    transaction, identity, policy, pact, and audit operations exposed by the
    Cobo Agentic Wallet service.  Use as an async context manager to ensure the
    underlying HTTP connection is closed on exit.
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None = None,
        allow_unauthenticated: bool = False,
        timeout: float = 30.0,
        service_auth_key: str | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._allow_unauthenticated = allow_unauthenticated
        self._timeout = timeout
        self._service_auth_key = service_auth_key

        # Initialize generated SDK client
        config = Configuration(
            host=self._base_url,
            api_key=api_key or "" if not allow_unauthenticated else "",
        )
        if service_auth_key:
            config.service_auth_key = service_auth_key
        # Set timeout (rest_async.py checks for this attribute)
        config.request_timeout = timeout
        self._api_client = AsyncApiClient(configuration=config)

        # Initialize API objects
        self._wallets_api = AsyncWalletsApi(api_client=self._api_client)
        self._transactions_api = AsyncTransactionsApi(api_client=self._api_client)
        self._transaction_records_api = AsyncTransactionRecordsApi(api_client=self._api_client)
        self._audit_api = AsyncAuditApi(api_client=self._api_client)
        self._identity_api = AsyncIdentityApi(api_client=self._api_client)
        self._health_api = AsyncHealthApi(api_client=self._api_client)
        self._meta_api = AsyncMetaApi(api_client=self._api_client)
        self._pending_operations_api = AsyncPendingOperationsApi(api_client=self._api_client)
        self._coin_price_api = AsyncCoinPriceApi(api_client=self._api_client)
        self._metadata_api = AsyncMetadataApi(api_client=self._api_client)
        self._faucet_api = AsyncFaucetApi(api_client=self._api_client)
        self._balance_api = AsyncBalanceApi(api_client=self._api_client)
        self._pacts_api = AsyncPactsApi(api_client=self._api_client)
        self._recipes_api = AsyncRecipesApi(api_client=self._api_client)
        self._suggestions_api = AsyncSuggestionsApi(api_client=self._api_client)
        self._telemetry_api = AsyncTelemetryApi(api_client=self._api_client)

    async def __aenter__(self) -> "WalletAPIClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

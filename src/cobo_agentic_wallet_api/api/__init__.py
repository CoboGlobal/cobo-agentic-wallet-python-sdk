# flake8: noqa

# TYPE_CHECKING imports for IDE support while maintaining lazy loading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import all API classes for IDE type checking and autocompletion
    from .audit_api import AuditApi
    from .balance_api import BalanceApi
    from .coin_price_api import CoinPriceApi
    from .faucet_api import FaucetApi
    from .health_api import HealthApi
    from .identity_api import IdentityApi
    from .meta_api import MetaApi
    from .metadata_api import MetadataApi
    from .pacts_api import PactsApi
    from .pending_operations_api import PendingOperationsApi
    from .recipes_api import RecipesApi
    from .script_tools_api import ScriptToolsApi
    from .suggestions_api import SuggestionsApi
    from .telemetry_api import TelemetryApi
    from .transaction_records_api import TransactionRecordsApi
    from .transactions_api import TransactionsApi
    from .wallets_api import WalletsApi

    # Import all Async API classes for IDE type checking and autocompletion
    from .audit_api_async import AsyncAuditApi
    from .balance_api_async import AsyncBalanceApi
    from .coin_price_api_async import AsyncCoinPriceApi
    from .faucet_api_async import AsyncFaucetApi
    from .health_api_async import AsyncHealthApi
    from .identity_api_async import AsyncIdentityApi
    from .meta_api_async import AsyncMetaApi
    from .metadata_api_async import AsyncMetadataApi
    from .pacts_api_async import AsyncPactsApi
    from .pending_operations_api_async import AsyncPendingOperationsApi
    from .recipes_api_async import AsyncRecipesApi
    from .script_tools_api_async import AsyncScriptToolsApi
    from .suggestions_api_async import AsyncSuggestionsApi
    from .telemetry_api_async import AsyncTelemetryApi
    from .transaction_records_api_async import AsyncTransactionRecordsApi
    from .transactions_api_async import AsyncTransactionsApi
    from .wallets_api_async import AsyncWalletsApi


# API classes mapping for lazy import
_API_CLASSES = {
    "AuditApi": "audit_api",
    "BalanceApi": "balance_api",
    "CoinPriceApi": "coin_price_api",
    "FaucetApi": "faucet_api",
    "HealthApi": "health_api",
    "IdentityApi": "identity_api",
    "MetaApi": "meta_api",
    "MetadataApi": "metadata_api",
    "PactsApi": "pacts_api",
    "PendingOperationsApi": "pending_operations_api",
    "RecipesApi": "recipes_api",
    "ScriptToolsApi": "script_tools_api",
    "SuggestionsApi": "suggestions_api",
    "TelemetryApi": "telemetry_api",
    "TransactionRecordsApi": "transaction_records_api",
    "TransactionsApi": "transactions_api",
    "WalletsApi": "wallets_api",
}

# Async API classes mapping for lazy import
_ASYNC_API_CLASSES = {
    "AsyncAuditApi": "audit_api_async",
    "AsyncBalanceApi": "balance_api_async",
    "AsyncCoinPriceApi": "coin_price_api_async",
    "AsyncFaucetApi": "faucet_api_async",
    "AsyncHealthApi": "health_api_async",
    "AsyncIdentityApi": "identity_api_async",
    "AsyncMetaApi": "meta_api_async",
    "AsyncMetadataApi": "metadata_api_async",
    "AsyncPactsApi": "pacts_api_async",
    "AsyncPendingOperationsApi": "pending_operations_api_async",
    "AsyncRecipesApi": "recipes_api_async",
    "AsyncScriptToolsApi": "script_tools_api_async",
    "AsyncSuggestionsApi": "suggestions_api_async",
    "AsyncTelemetryApi": "telemetry_api_async",
    "AsyncTransactionRecordsApi": "transaction_records_api_async",
    "AsyncTransactionsApi": "transactions_api_async",
    "AsyncWalletsApi": "wallets_api_async",
}


def __getattr__(name):
    """Lazy import for API classes and Async API classes."""
    if name in _API_CLASSES:
        module_name = f"cobo_agentic_wallet_api.api.{_API_CLASSES[name]}"
        module = __import__(module_name, fromlist=[name])
        attr = getattr(module, name)
        globals()[name] = attr
        return attr
    elif name in _ASYNC_API_CLASSES:
        module_name = f"cobo_agentic_wallet_api.api.{_ASYNC_API_CLASSES[name]}"
        module = __import__(module_name, fromlist=[name])
        attr = getattr(module, name)
        globals()[name] = attr
        return attr
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """Support for autocompletion."""
    return list(globals().keys()) + list(_API_CLASSES.keys()) + list(_ASYNC_API_CLASSES.keys())

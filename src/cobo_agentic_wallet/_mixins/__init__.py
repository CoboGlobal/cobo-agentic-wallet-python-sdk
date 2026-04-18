"""Mixin classes for WalletAPIClient (auto-generated)."""

from cobo_agentic_wallet._mixins.base import BaseClient
from cobo_agentic_wallet._mixins.audit import AuditMixin
from cobo_agentic_wallet._mixins.balance import BalanceMixin
from cobo_agentic_wallet._mixins.coin_price import CoinPriceMixin
from cobo_agentic_wallet._mixins.faucet import FaucetMixin
from cobo_agentic_wallet._mixins.health import HealthMixin
from cobo_agentic_wallet._mixins.identity import IdentityMixin
from cobo_agentic_wallet._mixins.metadata import MetadataMixin
from cobo_agentic_wallet._mixins.pact import PactMixin
from cobo_agentic_wallet._mixins.pending_operation import PendingOperationMixin
from cobo_agentic_wallet._mixins.recipe import RecipeMixin
from cobo_agentic_wallet._mixins.suggestion import SuggestionMixin
from cobo_agentic_wallet._mixins.telemetry import TelemetryMixin
from cobo_agentic_wallet._mixins.transaction_record import TransactionRecordMixin
from cobo_agentic_wallet._mixins.transaction import TransactionMixin
from cobo_agentic_wallet._mixins.wallet import WalletMixin

# Composite mixin that includes all functionality
AllMixins = (
    AuditMixin,
    BalanceMixin,
    CoinPriceMixin,
    FaucetMixin,
    HealthMixin,
    IdentityMixin,
    MetadataMixin,
    PactMixin,
    PendingOperationMixin,
    RecipeMixin,
    SuggestionMixin,
    TelemetryMixin,
    TransactionRecordMixin,
    TransactionMixin,
    WalletMixin,
)

__all__ = [
    "BaseClient",
    "AuditMixin",
    "BalanceMixin",
    "CoinPriceMixin",
    "FaucetMixin",
    "HealthMixin",
    "IdentityMixin",
    "MetadataMixin",
    "PactMixin",
    "PendingOperationMixin",
    "RecipeMixin",
    "SuggestionMixin",
    "TelemetryMixin",
    "TransactionRecordMixin",
    "TransactionMixin",
    "WalletMixin",
    "AllMixins",
]

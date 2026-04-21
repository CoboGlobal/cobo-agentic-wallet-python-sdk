"""Cobo Agentic Wallet SDK — async Python client for the Agentic Wallet REST API."""

from cobo_agentic_wallet.client import WalletAPIClient
from cobo_agentic_wallet_api.models.policy_scope import PolicyScope
from cobo_agentic_wallet_api.models.policy_type import PolicyType
from cobo_agentic_wallet_api.models.principal_type import PrincipalType
from cobo_agentic_wallet_api.models.vault_group_type import VaultGroupType
from cobo_agentic_wallet_api.models.wallet_type import WalletType
from cobo_agentic_wallet.errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    PolicyDenial,
    PolicyDeniedError,
    ServerError,
)
from cobo_agentic_wallet.toolkit import AgentWalletToolkit, ToolDefinition

try:
    from importlib.metadata import version as _version

    __version__ = _version("cobo-agentic-wallet")
except Exception:
    __version__ = "0.0.0"

__all__ = [
    "APIError",
    "AgentWalletToolkit",
    "AuthenticationError",
    "NotFoundError",
    "PolicyDenial",
    "PolicyDeniedError",
    "PolicyScope",
    "PolicyType",
    "PrincipalType",
    "WalletAPIClient",
    "ServerError",
    "ToolDefinition",
    "VaultGroupType",
    "WalletType",
    "__version__",
]

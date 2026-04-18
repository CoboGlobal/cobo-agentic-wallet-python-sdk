"""Error hierarchy and PolicyDenial dataclass for the Cobo Agentic Wallet SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

POLICY_ERROR_CODES: frozenset[str] = frozenset(
    {
        "TRANSFER_LIMIT_EXCEEDED",
        "BUSINESS_HOURS_VIOLATION",
        "CHAIN_RESTRICTED",
        "CONTRACT_NOT_WHITELISTED",
        "PARAMETER_OUT_OF_BOUNDS",
        "DELEGATION_EXPIRED",
        "WALLET_FROZEN",
        "INSUFFICIENT_BALANCE",
        "INSUFFICIENT_PERMISSION",
        "POLICY_DENIED",
    }
)


class APIError(Exception):
    """Base error for all Cobo Agentic Wallet API failures."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response_body: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body


class AuthenticationError(APIError):
    """Raised on HTTP 401."""


class NotFoundError(APIError):
    """Raised on HTTP 404."""


class ServerError(APIError):
    """Raised on HTTP 5xx."""


@dataclass(frozen=True)
class PolicyDenial:
    """Structured representation of a 403 policy denial."""

    code: str
    reason: str
    details: dict[str, Any]
    suggestion: str | None
    raw_response: dict[str, Any]

    @classmethod
    def try_from_response(cls, body: dict[str, Any] | None) -> PolicyDenial | None:
        """Parse structured policy denials only; return None for generic 403 responses."""

        if not isinstance(body, dict):
            return None

        error = body.get("error", body)
        if not isinstance(error, dict):
            return None

        code = error.get("code")
        if not isinstance(code, str) or code not in POLICY_ERROR_CODES:
            return None

        reason = error.get("reason")
        details = error.get("details")
        suggestion = error.get("suggestion")
        return cls(
            code=code,
            reason=str(reason) if reason is not None else "",
            details=details if isinstance(details, dict) else {},
            suggestion=str(suggestion) if suggestion is not None else None,
            raw_response=body,
        )


class PolicyDeniedError(APIError):
    """Raised on HTTP 403 — carries a PolicyDenial."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 403,
        response_body: dict[str, Any] | None = None,
        denial: PolicyDenial,
    ) -> None:
        super().__init__(message, status_code=status_code, response_body=response_body)
        self.denial = denial

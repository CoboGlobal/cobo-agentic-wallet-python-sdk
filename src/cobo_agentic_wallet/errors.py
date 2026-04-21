"""Error hierarchy and PolicyDenial dataclass for the Cobo Agentic Wallet SDK."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from cobo_agentic_wallet_api.exceptions import ApiException

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
        # `suggestion` may live either inside `error` or at the top level of the
        # response envelope, depending on which backend path raised it. Prefer
        # the top-level value when both exist so responses like
        # `{"error": {...}, "suggestion": "..."}` surface the hint to callers.
        suggestion = body.get("suggestion") or error.get("suggestion")
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


def translate_api_exception(exc: ApiException) -> APIError:
    """Translate a generated ``ApiException`` into the high-level ``APIError`` hierarchy.

    Parses ``exc.body`` as JSON and routes to:

    * ``PolicyDeniedError`` whenever the body carries a recognised policy
      ``code`` (see :data:`POLICY_ERROR_CODES`) — typically 403 policy denials
      such as ``TRANSFER_LIMIT_EXCEEDED`` / ``INSUFFICIENT_PERMISSION``.
    * ``AuthenticationError`` on HTTP 401.
    * ``NotFoundError`` on HTTP 404.
    * ``ServerError`` on HTTP 5xx.
    * ``APIError`` otherwise.
    """

    body_dict: dict[str, Any] | None = None
    raw_body = getattr(exc, "body", None)
    if isinstance(raw_body, (str, bytes, bytearray)):
        try:
            body_dict = json.loads(raw_body)
        except (TypeError, ValueError):
            body_dict = None
    elif isinstance(raw_body, dict):
        body_dict = raw_body

    denial = PolicyDenial.try_from_response(body_dict)
    status = int(getattr(exc, "status", 0) or 0)
    message = str(exc)

    if denial is not None:
        return PolicyDeniedError(
            message,
            status_code=status or 403,
            response_body=body_dict,
            denial=denial,
        )
    if status == 401:
        return AuthenticationError(message, status_code=status, response_body=body_dict)
    if status == 404:
        return NotFoundError(message, status_code=status, response_body=body_dict)
    if 500 <= status < 600:
        return ServerError(message, status_code=status, response_body=body_dict)
    return APIError(message, status_code=status, response_body=body_dict)

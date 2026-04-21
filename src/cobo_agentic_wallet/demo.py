"""Quickstart demo runner for Phase P11.

Demo logic (7 steps)
-------------------
Step 1 — Backend health check
  - GET /api/v1/ping with bootstrap client (no API key). Ensures backend is up.

Step 2 — Create principals (bootstrap; requires service credential)
  - POST /api/v1/principals x2: one "human" (owner), one "agent" (operator).
  - Backend requires header X-Assistant-Service-Key = SERVICE_AUTH_KEY (no user API key yet).
  - Without this header or with wrong value → 401 "Invalid service credential".

Step 3 — Create API keys (bootstrap; requires service credential)
  - POST /api/v1/api-keys x2: one for owner, one for agent (body.principal_id from step 2).
  - Same service credential required. Response contains raw_key (only shown once).

Step 4 — Create wallet + delegation
  - owner_client (X-API-Key: owner key): POST wallet, POST address, POST delegation.
  - Delegation grants operator "write:transfer" with limits (e.g. max 100/tx, 500/day).

Step 5 — Allowed transfer
  - operator_client: POST transfer amount 50 (within limit). Expect 200 + transaction.

Step 6 — Denied transfer (policy)
  - operator_client: POST transfer amount 200 (exceeds max_per_tx 100). Expect PolicyDeniedError 403.

Step 7 — Audit verification
  - owner_client: GET audit-logs filtered by wallet, principal_id=operator (no action filter).
  - Poll until we see both: (1) transfer.initiate result=allowed, (2) transfer.denied result=denied.
  - Policy denials are logged as action=transfer.denied; permission checks as transfer.initiate.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any
from uuid import uuid4

import httpx

from cobo_agentic_wallet.client import WalletAPIClient
from cobo_agentic_wallet.errors import APIError, PolicyDeniedError
from cobo_agentic_wallet.toolkit import AgentWalletToolkit

_DEMO_WALLET_NAME = "P11 Demo Wallet"
_DEMO_CHAIN_ID = "ETH"
_DEMO_TOKEN_ID = "SETH"
_DEMO_SUCCESS_AMOUNT = "50"
_DEMO_DENIAL_AMOUNT = "200"
_DEMO_MAX_PER_TX = "100"
_DEMO_DAILY_LIMIT = "500"
_DEMO_MONTHLY_LIMIT = "500"
_DEMO_DESTINATION = "0x1111111111111111111111111111111111111111"
_DEMO_COMPLETE_MESSAGE = "Your first guardrailed agent transaction in under 5 minutes!"
_BACKEND_START_SUGGESTION = "Start backend with: cd cobo-agent-wallet && docker-compose up -d"

# Audit: backend logs permission check as transfer.initiate (allowed); policy denial as transfer.denied (denied).
_DEMO_AUDIT_ALLOWED_ACTION = "transfer.initiate"
_DEMO_AUDIT_DENIED_ACTION = "transfer.denied"


class DemoError(RuntimeError):
    """Base class for quickstart demo failures."""


class DemoBackendUnavailableError(DemoError):
    """Raised when the backend is not reachable."""

    def __init__(self, message: str, *, suggestion: str) -> None:
        super().__init__(message)
        self.suggestion = suggestion


class DemoExecutionError(DemoError):
    """Raised when the demo workflow fails mid-execution."""


# ------------------------------------------------------------------
# Formatter functions (backported from B, adapted for A's dict shape)
# ------------------------------------------------------------------


def format_demo_output(result: dict[str, Any]) -> str:
    """Format demo result dict as human-readable text with numbered steps and [OK] markers."""
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("  Cobo Agent Wallet -- Quickstart Demo")
    lines.append("=" * 60)
    lines.append("")

    lines.append("  [OK] Step 1: Backend health check")

    owner_id = result.get("owner_principal_id", "?")
    agent_id = result.get("agent_principal_id", "?")
    lines.append("  [OK] Step 2: Create principals")
    lines.append(f"         Owner:  {owner_id}")
    lines.append(f"         Agent:  {agent_id}")

    lines.append("  [OK] Step 3: Create API keys")

    wallet_uuid = result.get("wallet_uuid", "?")
    delegation_id = result.get("delegation_id", "?")
    lines.append("  [OK] Step 4: Create wallet + delegation")
    lines.append(f"         Wallet UUID:    {wallet_uuid}")
    lines.append(f"         Delegation ID:  {delegation_id}")

    transfer_success = result.get("transfer_success", {})
    tx_status = transfer_success.get("status", "?") if isinstance(transfer_success, dict) else "?"
    lines.append(f"  [OK] Step 5: Transfer ${_DEMO_SUCCESS_AMOUNT} (within limit)")
    lines.append(f"         Status: {tx_status}")

    denial = result.get("transfer_denial", {})
    denial_code = denial.get("code", "?") if isinstance(denial, dict) else "?"
    denial_reason = denial.get("reason", "?") if isinstance(denial, dict) else "?"
    denial_suggestion = denial.get("suggestion") if isinstance(denial, dict) else None
    denial_details = denial.get("details") if isinstance(denial, dict) else None
    lines.append(f"  [OK] Step 6: Transfer ${_DEMO_DENIAL_AMOUNT} (exceeds limit)")
    lines.append(f"         Code:   {denial_code}")
    lines.append(f"         Reason: {denial_reason}")
    if isinstance(denial_suggestion, str) and denial_suggestion:
        lines.append(f"         Suggestion: {denial_suggestion}")
    if isinstance(denial_details, dict) and denial_details:
        lines.append(
            f"         Details: {json.dumps(denial_details, sort_keys=True, ensure_ascii=True)}"
        )

    audit_log = result.get("audit_log", {})
    allowed = audit_log.get("allowed_count", 0) if isinstance(audit_log, dict) else 0
    denied = audit_log.get("denied_count", 0) if isinstance(audit_log, dict) else 0
    lines.append("  [OK] Step 7: Audit log verification")
    lines.append(f"         Allowed: {allowed}  Denied: {denied}")

    lines.append("")
    lines.append("  Completed 7/7 steps.")
    message = result.get("message", "")
    if message:
        lines.append(f"  {message}")
    lines.append("=" * 60)
    return "\n".join(lines)


def format_demo_json(result: dict[str, Any]) -> dict[str, Any]:
    """Passthrough — identity function for symmetry with format_demo_output."""
    return result


# ------------------------------------------------------------------
# Audit polling helper (kept from A)
# ------------------------------------------------------------------


async def _wait_for_audit_entries(
    *,
    owner_client: WalletAPIClient,
    wallet_uuid: str,
    principal_id: str,
    max_attempts: int = 20,
    delay_seconds: float = 0.25,
) -> list[dict[str, Any]]:
    """Poll audit logs until we see both an allowed and a denied transfer.

    Backend logs permission check as transfer.initiate (allowed) and policy
    denial as transfer.denied (denied). We do not filter by action so both appear.
    """
    latest_entries: list[dict[str, Any]] = []
    for _ in range(max_attempts):
        page = await owner_client.list_audit_logs(
            wallet_id=wallet_uuid,
            principal_id=principal_id,
            limit=50,
        )

        if isinstance(page, list):
            entries = page
        elif isinstance(page, dict):
            entries = page.get("items", [])
        else:
            entries = []
        if isinstance(entries, list):
            latest_entries = [e for e in entries if isinstance(e, dict)]
            allowed = any(
                str(e.get("action", "")) == _DEMO_AUDIT_ALLOWED_ACTION
                and str(e.get("result", "")).lower() == "allowed"
                for e in latest_entries
            )
            denied = any(
                str(e.get("action", "")) == _DEMO_AUDIT_DENIED_ACTION
                and str(e.get("result", "")).lower() == "denied"
                for e in latest_entries
            )
            if allowed and denied:
                return latest_entries

        await asyncio.sleep(delay_seconds)

    return latest_entries


# ------------------------------------------------------------------
# Main demo runner (refactored: SDK client calls instead of raw httpx)
# ------------------------------------------------------------------


async def run_quickstart_demo(
    *,
    api_url: str,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Run the P11 quickstart demo workflow and return a structured summary."""
    normalized_api_url = api_url.rstrip("/")
    suffix = uuid4().hex[:8]

    key = os.environ.get("SERVICE_AUTH_KEY", "dev-assistant-service-key")

    # Step 1: Health check via unauthenticated SDK client
    bootstrap_client = WalletAPIClient(
        base_url=normalized_api_url,
        timeout=timeout,
        allow_unauthenticated=True,
        service_auth_key=key,
    )
    try:
        await bootstrap_client.ping()
    except (httpx.ConnectError, httpx.TimeoutException):
        raise DemoBackendUnavailableError(
            "AgentWallet backend is not reachable.",
            suggestion=_BACKEND_START_SUGGESTION,
        )
    except Exception as exc:
        raise DemoBackendUnavailableError(
            f"AgentWallet backend health check failed: {exc}",
            suggestion=_BACKEND_START_SUGGESTION,
        )

    # Step 2-3: Create principals and API keys via unauthenticated client
    try:
        owner_principal = await bootstrap_client.create_principal(
            external_id=f"demo-owner-{suffix}",
            principal_type="human",
            name="P11 Demo Owner",
        )
        if not isinstance(owner_principal, dict) or "id" not in owner_principal:
            raise DemoExecutionError("create owner principal returned invalid payload")
        owner_principal_id = owner_principal["id"]

        operator_principal = await bootstrap_client.create_principal(
            external_id=f"demo-agent-{suffix}",
            principal_type="agent",
            name="P11 Demo Agent",
        )
        if not isinstance(operator_principal, dict) or "id" not in operator_principal:
            raise DemoExecutionError("create agent principal returned invalid payload")
        operator_principal_id = operator_principal["id"]

        owner_key_result = await bootstrap_client.create_api_key(
            principal_id=owner_principal_id,
            name=f"demo-owner-{suffix}-key",
            scopes=["*"],
        )
        if not isinstance(owner_key_result, dict) or "raw_key" not in owner_key_result:
            raise DemoExecutionError("create owner api key returned invalid payload")
        owner_api_key = owner_key_result["raw_key"]

        operator_key_result = await bootstrap_client.create_api_key(
            principal_id=operator_principal_id,
            name=f"demo-agent-{suffix}-key",
            scopes=["*"],
        )
        if not isinstance(operator_key_result, dict) or "raw_key" not in operator_key_result:
            raise DemoExecutionError("create agent api key returned invalid payload")
        operator_api_key = operator_key_result["raw_key"]
    finally:
        await bootstrap_client.close()

    # Step 4-7: Wallet ops via authenticated clients
    owner_client = WalletAPIClient(
        base_url=normalized_api_url,
        api_key=owner_api_key,
        timeout=timeout,
    )
    operator_client = WalletAPIClient(
        base_url=normalized_api_url,
        api_key=operator_api_key,
        timeout=timeout,
    )
    try:
        wallet = await owner_client.create_wallet(
            name=_DEMO_WALLET_NAME,
            wallet_type="Custodial-Web3",
            metadata={"source": "p11-demo", "run_id": suffix},
        )
        if not isinstance(wallet, dict):
            raise DemoExecutionError("create wallet returned invalid payload")
        wallet_uuid = wallet.get("uuid")
        if not isinstance(wallet_uuid, str):
            raise DemoExecutionError("create wallet returned invalid uuid")

        address = await owner_client.create_wallet_address(
            wallet_uuid,
            chain_identifier=_DEMO_CHAIN_ID,
        )

        delegation = await owner_client.create_delegation(
            operator_id=operator_principal_id,
            wallet_id=wallet_uuid,
            permissions=["write:transfer"],
            constraints={
                "max_per_tx": _DEMO_MAX_PER_TX,
                "daily_cumulative": _DEMO_DAILY_LIMIT,
                "monthly_cumulative": _DEMO_MONTHLY_LIMIT,
            },
        )
        if not isinstance(delegation, dict):
            raise DemoExecutionError("create delegation returned invalid payload")

        success_transfer = await operator_client.transfer_tokens(
            wallet_uuid,
            chain_id=_DEMO_CHAIN_ID,
            dst_addr=_DEMO_DESTINATION,
            token_id=_DEMO_TOKEN_ID,
            amount=_DEMO_SUCCESS_AMOUNT,
            request_id=f"p11-success-{suffix}",
        )

        denied_transfer: dict[str, Any]
        try:
            await operator_client.transfer_tokens(
                wallet_uuid,
                chain_id=_DEMO_CHAIN_ID,
                dst_addr=_DEMO_DESTINATION,
                token_id=_DEMO_TOKEN_ID,
                amount=_DEMO_DENIAL_AMOUNT,
                request_id=f"p11-denied-{suffix}",
            )
        except PolicyDeniedError as exc:
            denied_transfer = {
                "error": "POLICY_DENIED",
                "code": exc.denial.code,
                "reason": exc.denial.reason,
                "details": exc.denial.details,
                "suggestion": exc.denial.suggestion,
                "formatted": AgentWalletToolkit._format_denial(exc.denial),
            }
        except APIError as exc:
            raise DemoExecutionError(
                f"expected policy denial for high-value transfer, got API error {exc.status_code}: {exc}"
            ) from exc
        else:
            raise DemoExecutionError(
                "expected policy denial for high-value transfer, but transfer was allowed"
            )

        audit_entries = await _wait_for_audit_entries(
            owner_client=owner_client,
            wallet_uuid=wallet_uuid,
            principal_id=operator_principal_id,
        )
        allowed_count = sum(
            1
            for e in audit_entries
            if str(e.get("action", "")) == _DEMO_AUDIT_ALLOWED_ACTION
            and str(e.get("result", "")).lower() == "allowed"
        )
        denied_count = sum(
            1
            for e in audit_entries
            if str(e.get("action", "")) == _DEMO_AUDIT_DENIED_ACTION
            and str(e.get("result", "")).lower() == "denied"
        )
        if allowed_count < 1 or denied_count < 1:
            raise DemoExecutionError(
                "audit log did not contain both allowed and denied transfer entries in time"
            )

        return {
            "owner_principal_id": owner_principal_id,
            "agent_principal_id": operator_principal_id,
            "wallet_uuid": wallet_uuid,
            "wallet_address": address,
            "delegation_id": delegation.get("id"),
            "transfer_success": success_transfer,
            "transfer_denial": denied_transfer,
            "audit_log": {
                "allowed_count": allowed_count,
                "denied_count": denied_count,
                "entries": audit_entries,
            },
            "message": _DEMO_COMPLETE_MESSAGE,
        }
    finally:
        await owner_client.close()
        await operator_client.close()

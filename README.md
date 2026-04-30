# Cobo Agentic Wallet Python SDK

Python SDK, MCP server, and agent-framework integrations for Cobo Agentic Wallet.

This SDK is for developers building AI agents, bots, and automations that:

- move funds
- make payments
- sign messages
- interact with smart contracts
- need scoped authorization instead of raw wallet custody

Instead of giving an agent a private key, Cobo Agentic Wallet gives it a controlled runtime surface:

- pair once with the wallet owner
- submit a pact to define what the agent is allowed to do
- operate within owner-approved boundaries
- receive structured denial feedback when a request is blocked
- keep signing and key management outside the agent runtime

[![PyPI version](https://img.shields.io/pypi/v/cobo-agentic-wallet)](https://pypi.org/project/cobo-agentic-wallet/)
[![Python versions](https://img.shields.io/pypi/pyversions/cobo-agentic-wallet)](https://pypi.org/project/cobo-agentic-wallet/)
[![License](https://img.shields.io/github/license/CoboGlobal/cobo-agentic-wallet-python-sdk)](https://github.com/CoboGlobal/cobo-agentic-wallet-python-sdk/blob/master/LICENSE)

## AI coding agent support

If you are building with an AI coding agent (Claude Code, Cursor, Windsurf, etc.), install the CAW developer skill to give it context on the SDK and CLI:

```bash
npx skills add CoboGlobal/cobo-agentic-wallet --skill cobo-agentic-wallet-developer --yes --global
```

## Related repositories

- [CAW TypeScript SDK](https://github.com/CoboGlobal/cobo-agentic-wallet-typescript-sdk)
- [CAW CLI](https://github.com/CoboGlobal/cobo-agentic-wallet-cli)

## What this repo includes

- **Python SDK** (`WalletAPIClient`) — async client for wallet, pact, transaction, and audit operations
- **MCP server** — expose wallet tools to any MCP-compatible host (Claude Desktop, Cursor, etc.)
- **Framework integrations** — LangChain, OpenAI Agents SDK, Agno, CrewAI; narrow the tool surface with `include_tools` / `exclude_tools`
- **Examples** — runnable examples under [`examples/`](examples/)

## Get Started

Before using this SDK, follow the [Get Started guide](https://github.com/CoboGlobal/cobo-agentic-wallet#get-started) in the main repo to install the `caw` CLI, onboard, and get your credentials.

### 1. Install the SDK

```bash
pip install cobo-agentic-wallet
```

### 2. Submit a pact and run a transfer

```python
import asyncio
import os
import time

from cobo_agentic_wallet.client import WalletAPIClient
from cobo_agentic_wallet.errors import PolicyDeniedError

CHAIN_ID = "SETH"
TOKEN_ID = "SETH"
ALLOWED_AMOUNT = "0.001"
DENIED_AMOUNT = "0.005"
DENY_THRESHOLD = "0.002"


async def main() -> None:
    api_url = os.environ["AGENT_WALLET_API_URL"]
    api_key = os.environ["AGENT_WALLET_API_KEY"]
    wallet_id = os.environ["AGENT_WALLET_WALLET_ID"]
    destination = os.environ.get(
        "CAW_DESTINATION",
        "0x1111111111111111111111111111111111111111",
    )

    client = WalletAPIClient(base_url=api_url, api_key=api_key)

    try:
        # Step 1: Submit a pact requesting transfer permissions for 24 hours.
        print(
            f"[1/6] Submitting pact (allow {CHAIN_ID}/{TOKEN_ID} transfers, "
            f"deny if amount > {DENY_THRESHOLD})..."
        )
        pact_resp = await client.submit_pact(
            wallet_id=wallet_id,
            intent="Transfer tokens for integration testing",
            spec={
                "policies": [
                    {
                        "name": "max-tx-limit",
                        "type": "transfer",
                        "rules": {
                            "effect": "allow",
                            "when": {
                                "chain_in": [CHAIN_ID],
                                "token_in": [{"chain_id": CHAIN_ID, "token_id": TOKEN_ID}],
                            },
                            "deny_if": {"amount_gt": DENY_THRESHOLD},
                        },
                    }
                ],
                "completion_conditions": [
                    {"type": "time_elapsed", "threshold": "86400"}
                ],
            },
        )
        pact_id = pact_resp["pact_id"]
        print(f"      pact submitted: id={pact_id}")

        # Step 2: Poll until the owner approves the pact.
        print("[2/6] Waiting for owner approval in the Cobo Agentic Wallet app...")
        started = time.monotonic()
        last_status = None
        while True:
            pact = await client.get_pact(pact_id)
            status = pact.get("status", "")
            if status != last_status:
                elapsed = int(time.monotonic() - started)
                print(f"      pact status -> {status} (elapsed {elapsed}s)")
                last_status = status
            if status == "active":
                break
            if status in ("rejected", "expired", "revoked", "completed"):
                raise RuntimeError(f"Pact reached terminal status before use: {status}")
            await asyncio.sleep(5)

        # Step 3: Use the pact-scoped API key for all subsequent calls.
        print("[3/6] Pact is active; switching to pact-scoped API key.")
        pact_api_key = pact["api_key"]
        pact_client = WalletAPIClient(base_url=api_url, api_key=pact_api_key)

        try:
            # Step 4: Execute an allowed transfer (within the deny threshold).
            print(
                f"[4/6] Submitting allowed transfer: {ALLOWED_AMOUNT} {TOKEN_ID} -> {destination}"
            )
            allowed = await pact_client.transfer_tokens(
                wallet_id,
                chain_id=CHAIN_ID,
                dst_addr=destination,
                token_id=TOKEN_ID,
                amount=ALLOWED_AMOUNT,
            )
            print(
                f"      ALLOWED: tx_id={allowed.get('id')} "
                f"status={allowed.get('status')} ({allowed.get('status_display') or '-'}) "
                f"request_id={allowed.get('request_id')} "
                f"hash={allowed.get('transaction_hash') or '-'}"
            )

            # Step 5: Trigger a policy denial (amount exceeds the deny threshold),
            # then follow the denial guidance and retry with a compliant amount.
            print(
                f"[5/6] Submitting transfer that should be blocked: "
                f"{DENIED_AMOUNT} {TOKEN_ID} -> {destination}"
            )
            try:
                await pact_client.transfer_tokens(
                    wallet_id,
                    chain_id=CHAIN_ID,
                    dst_addr=destination,
                    token_id=TOKEN_ID,
                    amount=DENIED_AMOUNT,
                )
            except PolicyDeniedError as exc:
                denial = exc.denial
                print(
                    f"      DENIED as expected: http={exc.status_code} "
                    f"code={denial.code} reason={denial.reason}"
                )
                if denial.details:
                    print(f"      details: {denial.details}")
                if denial.suggestion:
                    print(f"      suggestion: {denial.suggestion}")

                print(
                    f"      retrying with compliant amount {ALLOWED_AMOUNT} {TOKEN_ID}..."
                )
                retry = await pact_client.transfer_tokens(
                    wallet_id,
                    chain_id=CHAIN_ID,
                    dst_addr=destination,
                    token_id=TOKEN_ID,
                    amount=ALLOWED_AMOUNT,
                )
                print(
                    f"      RETRY ALLOWED: tx_id={retry.get('id')} "
                    f"status={retry.get('status')} ({retry.get('status_display') or '-'}) "
                    f"request_id={retry.get('request_id')} "
                    f"hash={retry.get('transaction_hash') or '-'}"
                )
        finally:
            await pact_client.close()

        # Step 6: Verify allowed and denied events in audit logs.
        print("[6/6] Fetching recent audit entries for this wallet...")
        logs = await client.list_audit_logs(wallet_id=wallet_id, limit=20)
        items = logs.get("items", []) if isinstance(logs, dict) else []
        allowed_count = sum(1 for item in items if item.get("result") == "allowed")
        denied_count = sum(1 for item in items if item.get("result") == "denied")
        print(f"      audit (last {len(items)} entries): allowed={allowed_count}, denied={denied_count}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Add MCP or an agent framework

Use a framework only after the direct SDK flow works.

## MCP server

Run the stdio MCP server:

```bash
AGENT_WALLET_API_URL=https://api.agenticwallet.cobo.com \
AGENT_WALLET_API_KEY=your-api-key \
python -m cobo_agentic_wallet.mcp
```

Narrow the tool surface with `AGENT_WALLET_INCLUDE_TOOLS`:

```bash
AGENT_WALLET_INCLUDE_TOOLS=submit_pact,get_pact,transfer_tokens,get_transaction_record_by_request_id \
python -m cobo_agentic_wallet.mcp
```

Example Claude Desktop config:

```json
{
  "mcpServers": {
    "cobo-agentic-wallet": {
      "command": "python",
      "args": ["-m", "cobo_agentic_wallet.mcp"],
      "env": {
        "AGENT_WALLET_API_URL": "https://api.agenticwallet.cobo.com",
        "AGENT_WALLET_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Framework integrations

| Framework | Install | Entry point |
|---|---|---|
| LangChain | `pip install "cobo-agentic-wallet[langchain]"` | `from cobo_agentic_wallet.integrations.langchain import CoboAgentWalletToolkit` |
| OpenAI Agents SDK | `pip install "cobo-agentic-wallet[openai]"` | `from cobo_agentic_wallet.integrations.openai import create_cobo_agent` |
| Agno | `pip install "cobo-agentic-wallet[agno]"` | `from cobo_agentic_wallet.integrations.agno import CoboAgentWalletTools` |
| CrewAI | `pip install "cobo-agentic-wallet[crewai]"` | `from cobo_agentic_wallet.integrations.crewai import CoboAgentWalletCrewAIToolkit` |

All integrations support narrowing the tool surface with `include_tools` and `exclude_tools`.

Recommended presets:

- **Pact drafting**: `submit_pact`, `get_pact`, `list_pacts`
- **Execution**: `transfer_tokens`, `contract_call`, `estimate_transfer_fee`, `estimate_contract_call_fee`, `get_transaction_record_by_request_id`
- **Observer**: `list_wallets`, `get_wallet`, `get_balance`, `list_transaction_records`, `get_audit_logs`

## Examples

Runnable examples live under [`examples/`](examples/):

- [Direct SDK](examples/direct_sdk.py)
- [LangChain](examples/langchain_agent.py)
- [OpenAI Agents SDK](examples/openai_agent.py)
- [Agno](examples/agno_agent.py)
- [CrewAI](examples/crewai_agent.py)

## Contributing

1. Fork the repository and create a branch from `master`.
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Make your changes and run the linter:
   ```bash
   uv run ruff check src/
   ```
4. Open a pull request against `master` with a clear description of your change.

## License

Apache-2.0. See [LICENSE](LICENSE).
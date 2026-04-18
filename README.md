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

## Related repositories

- [CAW TypeScript SDK](https://github.com/CoboGlobal/cobo-agentic-wallet-typescript-sdk)
- [CAW CLI](https://github.com/CoboGlobal/cobo-agentic-wallet-cli)

## What this repo includes

- **Python SDK** (`WalletAPIClient`) — async client for wallet, pact, transaction, and audit operations
- **MCP server** — expose wallet tools to any MCP-compatible host (Claude Desktop, Cursor, etc.)
- **Framework integrations** — LangChain, OpenAI Agents SDK, Agno, CrewAI; narrow the tool surface with `include_tools` / `exclude_tools`
- **Examples** — runnable examples under [`examples/`](examples/)

## Get Started

### 1. Install the `caw` CLI

```bash
curl -fsSL https://raw.githubusercontent.com/CoboGlobal/cobo-agentic-wallet/master/install.sh | bash
```

Then add `caw` to your PATH:

```bash
export PATH="$HOME/.cobo-agentic-wallet/bin:$PATH"
```

Verify the installation:

```bash
caw --version
```

### 2. Onboard and pair with the wallet owner

Run the interactive onboarding wizard. You will need an invitation code from the wallet owner.

```bash
caw onboard --wait --invitation-code <invitation-code>
```

The wizard runs through several phases until wallet `status` becomes `active`.

Once the wallet is active, generate a pairing token for the wallet owner:

```bash
caw wallet pair --code-only
```

The wallet owner enters the token in the Cobo Agentic Wallet app to complete ownership pairing. Check pairing status with:

```bash
caw wallet pair-status
```

### 3. Claim testnet tokens from the faucet

```bash
# List addresses for the wallet
caw address list

# Request native Sepolia ETH
caw faucet deposit --token-id SETH --address <your-seth-address>
```

Check the balance with `caw wallet balance`.

### 4. Get credentials

```bash
caw wallet current --show-api-key
```

Set the output values as environment variables:

```bash
export AGENT_WALLET_API_URL=https://api.agenticwallet.cobo.com
export AGENT_WALLET_API_KEY=your-agent-api-key
export AGENT_WALLET_WALLET_ID=your-wallet-uuid
```

### 5. Install the SDK

```bash
pip install cobo-agentic-wallet
```

### 6. Submit a pact and run a transfer

```python
import asyncio
import os

from cobo_agentic_wallet import WalletAPIClient

CHAIN_ID = "SETH"
TOKEN_ID = "SETH"
DESTINATION = "0x1111111111111111111111111111111111111111"
ALLOWED_AMOUNT = "0.001"
DENY_THRESHOLD = "0.002"


async def main() -> None:
    api_url = os.environ["AGENT_WALLET_API_URL"]
    api_key = os.environ["AGENT_WALLET_API_KEY"]
    wallet_id = os.environ["AGENT_WALLET_WALLET_ID"]

    async with WalletAPIClient(base_url=api_url, api_key=api_key) as client:
        # Submit a pact requesting transfer permissions
        pact_resp = await client.submit_pact(
            wallet_id=wallet_id,
            intent="Transfer tokens for testing",
            spec={
                "policies": [
                    {
                        "name": "max-tx-limit",
                        "type": "transfer",
                        "rules": {
                            "effect": "allow",
                            "when": {"chain_in": [CHAIN_ID]},
                            "deny_if": {"amount_gt": DENY_THRESHOLD},
                        },
                    }
                ],
                "completion_conditions": [{"type": "time_elapsed", "threshold": "86400"}],
            },
        )
        pact_id = pact_resp["pact_id"]
        print(f"Pact submitted: {pact_id}")

        # Poll until the owner approves the pact
        while True:
            pact = await client.get_pact(pact_id)
            if pact["status"] == "active":
                break
            if pact["status"] in ("rejected", "expired", "revoked", "completed"):
                raise RuntimeError(f"Pact ended: {pact['status']}")
            await asyncio.sleep(5)

        # Execute a transfer using the pact-scoped API key
        async with WalletAPIClient(base_url=api_url, api_key=pact["api_key"]) as pact_client:
            tx = await pact_client.transfer_tokens(
                wallet_id,
                chain_id=CHAIN_ID,
                dst_addr=DESTINATION,
                token_id=TOKEN_ID,
                amount=ALLOWED_AMOUNT,
            )
            print(f"Transfer submitted: {tx['id']}")


if __name__ == "__main__":
    asyncio.run(main())
```

### 7. Add MCP or an agent framework

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
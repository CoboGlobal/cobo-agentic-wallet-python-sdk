# Getting Started

## Core Concepts

The Cobo Agentic Wallet SDK provides policy-aware wallet automation for AI agents and automated runtimes.

- Pact: task-scoped authorization approved by the wallet owner
- Pact-scoped API key: credential returned when a pact becomes active
- Policy: server-side rule enforcement with structured denial feedback
- Audit trail: transaction and policy history your runtime can inspect programmatically

## Canonical flow

1. pair with the wallet owner
2. use the direct SDK first
3. submit a pact
4. wait until it is active
5. execute a blockchain action
6. handle denial feedback and retry within the allowed boundary
7. add a framework or MCP only after that flow works

## Installation

Package metadata:

- Package name: `cobo-agentic-wallet`
- Python requirement: `>=3.11`

Install base SDK:

```bash
pip install cobo-agentic-wallet
```

Install integration extras:

```bash
pip install "cobo-agentic-wallet[langchain]"
pip install "cobo-agentic-wallet[openai]"
pip install "cobo-agentic-wallet[agno]"
pip install "cobo-agentic-wallet[crewai]"
```

## Environment

```python
export AGENT_WALLET_API_URL=https://api.agenticwallet.cobo.com
export AGENT_WALLET_API_KEY=your-api-key
export AGENT_WALLET_WALLET_ID=your-wallet-uuid
```

## Next Steps

- Run the direct example: `uv run python examples/python/direct_sdk.py`
- [LangChain Guide](./langchain.md)
- [OpenAI Agents SDK Guide](./openai.md)
- [Agno Guide](./agno.md)
- [CrewAI Guide](./crewai.md)
- [API Reference](../api-reference.md)

# CrewAI Guide

## Overview

The CrewAI integration builds dynamic `BaseTool` classes from canonical tool
schemas, enabling multi-agent role-based workflows.

Use the direct SDK pact flow first, then add the CrewAI layer.

## Install

```bash
pip install "cobo-agentic-wallet[crewai]"
```

## Quick Start

```python
from cobo_agentic_wallet.client import WalletAPIClient
from cobo_agentic_wallet.integrations.crewai import CoboAgentWalletCrewAIToolkit

client = WalletAPIClient(
    base_url="https://api.agenticwallet.cobo.com",
    api_key="<api_key>",
)
toolkit = CoboAgentWalletCrewAIToolkit(
    client=client,
    include_tools=[
        "submit_pact",
        "get_pact",
        "transfer_tokens",
        "estimate_transfer_fee",
        "get_transaction_record_by_request_id",
        "get_audit_logs",
    ],
)
tools = toolkit.get_tools()
```

## Denial Behavior

- Policy denials: returned as tool output
- Other API failures: raised as runtime errors

## Example

```bash
uv run --extra crewai python examples/python/crewai_agent.py
```

## Reference

- `src/cobo_agentic_wallet/integrations/crewai/toolkit.py`
- `examples/python/crewai_agent.py`

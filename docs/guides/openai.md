# OpenAI Agents SDK Guide

## Overview

The OpenAI integration exposes three levels:

1. `build_function_tools()` for raw function tools
2. `get_cobo_tools()` for bring-your-own agent
3. `create_cobo_agent()` for a preconfigured agent with denial-aware guidance

Use the direct SDK pact flow first, then add the OpenAI agent layer.

## Install

```bash
pip install "cobo-agentic-wallet[openai]"
```

## Quick Start

```python
from agents import Runner
from cobo_agentic_wallet.client import WalletAPIClient
from cobo_agentic_wallet.integrations.openai import create_cobo_agent, create_cobo_agent_context

client = WalletAPIClient(
    base_url="https://api.agenticwallet.cobo.com",
    api_key="<api_key>",
)
agent = create_cobo_agent(
    client=client,
    model="gpt-4.1-mini",
    include_tools=[
        "submit_pact",
        "get_pact",
        "transfer_tokens",
        "estimate_transfer_fee",
        "get_transaction_record_by_request_id",
        "get_audit_logs",
    ],
)
context = create_cobo_agent_context()
result = Runner.run_sync(
    agent,
    "Submit a pact first, then execute a compliant transfer.",
    context=context,
    max_turns=8,
)
print(result.final_output)
```

## Denial Behavior

Policy denials are preserved as structured guidance and fed back into subsequent
agent instructions for retry decisions.

## Recommended first subset

- `submit_pact`
- `get_pact`
- `transfer_tokens`
- `estimate_transfer_fee`
- `get_transaction_record_by_request_id`
- `get_audit_logs`

## Reference

- `src/cobo_agentic_wallet/integrations/openai/agent.py`
- `examples/python/openai_agent.py`

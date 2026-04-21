# Agno Guide

## Overview

The Agno integration exposes both sync and async tool surfaces and hydrates tool
metadata from canonical `ToolDefinition` schemas.

Use the direct SDK pact flow first, then add the Agno layer.

## Install

```bash
pip install "cobo-agentic-wallet[agno]"
```

## Quick Start

```python
from cobo_agentic_wallet.client import WalletAPIClient
from cobo_agentic_wallet.integrations.agno import CoboAgentWalletTools

client = WalletAPIClient(
    base_url="https://api.agenticwallet.cobo.com",
    api_key="<api_key>",
)
tools = CoboAgentWalletTools(
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
```

## Tool Selection

You can enable or disable specific tools via constructor flags or `include_tools` / `exclude_tools`.

## Denial Behavior

Policy denials are returned as readable output so agent logic can adjust and retry.

## Example

```bash
uv run python examples/python/agno_agent.py
```

## Reference

- `src/cobo_agentic_wallet/integrations/agno/toolkit.py`
- `examples/python/agno_agent.py`

# LangChain Guide

## Overview

The LangChain integration adapts Cobo wallet tools as `StructuredTool` instances.
Policy denials are returned as readable tool output so the agent can self-correct.

Use LangChain only after the direct SDK pact flow works.

## Install

```bash
pip install "cobo-agentic-wallet[langchain]" langchain-openai
```

## Quick Start

```python
from cobo_agentic_wallet.client import WalletAPIClient
from cobo_agentic_wallet.integrations.langchain import CoboAgentWalletToolkit

client = WalletAPIClient(
    base_url="https://api.agenticwallet.cobo.com",
    api_key="<api_key>",
)
toolkit = CoboAgentWalletToolkit(
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
tools = toolkit.get_tools()  # list[StructuredTool]
```

## Tools

The toolkit is built from the canonical CAW tool surface. In practice, you should expose only the subset the runtime needs.

Recommended first subset:

- `submit_pact`
- `get_pact`
- `transfer_tokens`
- `estimate_transfer_fee`
- `get_transaction_record_by_request_id`
- `get_audit_logs`

## Agent Executor

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Submit a pact before execution, wait until it is active, and if a tool returns "
        "a policy denial then retry only inside the suggested boundary.",
    ),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = executor.invoke({"input": "Submit a pact first, then execute a compliant transfer."})
```

## Denial Behavior

When a transfer is denied by policy, the tool returns formatted text instead of
raising an exception:

```
Policy Denied [TRANSFER_LIMIT_EXCEEDED]: max_per_tx
  limit_value: 100
  requested: 1000
Suggestion: Retry with amount <= 100.
```

The LLM reads this output and can retry with compliant parameters.

## Error Contract

- **Policy denials** → returned as formatted text (tool succeeds)
- **Other API errors** → raised as `ToolException` (tool fails, agent can retry)

## Reference

- `src/cobo_agentic_wallet/integrations/langchain/toolkit.py`
- `examples/python/langchain_agent.py`

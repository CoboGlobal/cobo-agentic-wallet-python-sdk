"""Agno example using the current pact-first CAW usage model."""

import asyncio
import os

from cobo_agentic_wallet import WalletAPIClient
from cobo_agentic_wallet.integrations.agno import CoboAgentWalletTools


def main() -> None:
    api_url = os.environ["AGENT_WALLET_API_URL"]
    api_key = os.environ["AGENT_WALLET_API_KEY"]
    wallet_uuid = os.environ["AGENT_WALLET_WALLET_ID"]
    destination = os.environ.get(
        "CAW_DESTINATION",
        "0x1111111111111111111111111111111111111111",
    )

    client = WalletAPIClient(
        base_url=api_url,
        api_key=api_key,
    )
    toolkit = CoboAgentWalletTools(
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

    try:
        print("Registered Cobo tools (sync):")
        for name in sorted(toolkit.functions.keys()):
            print(f"  - {name}")
        print("Registered Cobo tools (async):")
        for name in sorted(toolkit.async_functions.keys()):
            print(f"  - {name}")

        # Optional full agent run if Agno model deps and OPENAI_API_KEY are available.
        # This prompt is intentionally crafted to trigger policy self-correction behavior.
        if not os.getenv("OPENAI_API_KEY"):
            print("\nSet OPENAI_API_KEY to run a full Agno agent demo prompt.")
            return

        from agno.agent import Agent
        from agno.models.openai import OpenAIChat

        agent = Agent(
            model=OpenAIChat(id="gpt-4.1-mini"),
            tools=[toolkit],
            markdown=True,
        )

        prompt = (
            f"Use wallet {wallet_uuid}. "
            "Submit a pact first and wait until it becomes active. "
            f"Then transfer 50 USDC to {destination} on BASE. "
            "After that, attempt 200 USDC. If denied by policy, follow the suggestion and retry."
        )
        asyncio.run(agent.aprint_response(prompt))
    finally:
        asyncio.run(client.close())


if __name__ == "__main__":
    main()

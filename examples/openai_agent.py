"""OpenAI Agents SDK example using the current pact-first CAW usage model."""

import asyncio
import os

from cobo_agentic_wallet import WalletAPIClient
from cobo_agentic_wallet.integrations.openai import create_cobo_agent, create_cobo_agent_context


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

    try:
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
        print("Registered Cobo OpenAI tools:")
        for tool in agent.tools:
            name = getattr(tool, "name", tool.__class__.__name__)
            description = getattr(tool, "description", "")
            print(f"  - {name}: {description}")

        if not os.getenv("OPENAI_API_KEY"):
            print("\nSet OPENAI_API_KEY to run a full OpenAI agent demo prompt.")
            return

        try:
            from agents import Runner
        except ImportError as exc:
            raise RuntimeError(
                "openai-agents is required for this example. "
                "Install with: pip install 'cobo-agentic-wallet[openai]'"
            ) from exc

        prompt = (
            f"Use wallet {wallet_uuid}. "
            "Submit a pact for a controlled transfer task and wait until it is active. "
            f"Then transfer 50 USDC to {destination} on BASE. "
            "Next attempt 200 USDC. If denied, follow the denial guidance and retry with a "
            "compliant amount. "
            "Track the result by request_id and summarize what happened."
        )
        context = create_cobo_agent_context()
        result = Runner.run_sync(agent, prompt, context=context, max_turns=8)
        print("\nAgent result:", result.final_output)
    finally:
        asyncio.run(client.close())


if __name__ == "__main__":
    main()

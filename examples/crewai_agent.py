"""CrewAI example using the current pact-first CAW usage model."""

import asyncio
import os

from cobo_agentic_wallet import WalletAPIClient
from cobo_agentic_wallet.integrations.crewai import CoboAgentWalletCrewAIToolkit


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

    try:
        print("Registered CrewAI tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:60]}...")

        if not os.getenv("OPENAI_API_KEY"):
            print("\nSet OPENAI_API_KEY to run a full CrewAI multi-agent crew demo.")
            return

        try:
            from crewai import Agent, Crew, Process, Task
        except ImportError as exc:
            raise RuntimeError(
                "crewai is required for this example. Install with: pip install 'cobo-agentic-wallet[crewai]'"
            ) from exc

        operator = Agent(
            role="Wallet Operator",
            goal=(
                "Submit pacts and execute controlled transfers. "
                "If a transfer is denied by policy, read the denial suggestion "
                "and retry with compliant parameters."
            ),
            backstory=(
                "You operate inside CAW guardrails. You submit a pact before execution and "
                "adapt your next step based on policy feedback."
            ),
            tools=tools,
            verbose=True,
        )

        transfer_task = Task(
            description=(
                f"Use wallet {wallet_uuid}. Submit a pact first and wait until it is active. "
                f"Then transfer 50 USDC to {destination} on BASE. "
                "After that, attempt 200 USDC. If denied, follow the policy suggestion and retry. "
                "Finally summarize the outcome and mention the request tracking step."
            ),
            expected_output="A summary of the pact, transfer attempt, denial handling, and retry.",
            agent=operator,
        )

        crew = Crew(
            agents=[operator],
            tasks=[transfer_task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()
        print("\n--- Crew Result ---")
        print(result)
    finally:
        asyncio.run(client.close())


if __name__ == "__main__":
    main()

"""LangChain example using the current pact-first CAW usage model."""

import asyncio
import os

from cobo_agentic_wallet import WalletAPIClient
from cobo_agentic_wallet.integrations.langchain import CoboAgentWalletToolkit


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
    tools = toolkit.get_tools()

    try:
        print("Registered Cobo LangChain tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        if not os.getenv("OPENAI_API_KEY"):
            print(
                "\nSet OPENAI_API_KEY and install langchain-openai to run a full agent demo prompt."
            )
            return

        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise RuntimeError(
                "langchain-openai is required for the OpenAI model example. "
                "Install with: pip install langchain-openai"
            ) from exc

        prompt = (
            f"Use wallet {wallet_uuid}. "
            "First submit a pact for a controlled transfer task and wait until it is active. "
            f"Then transfer 50 USDC to {destination} on BASE. "
            "After that, attempt 200 USDC. If denied by policy, use the denial suggestion "
            "to retry with a compliant amount. "
            f"Finally inspect audit logs for wallet {wallet_uuid}."
        )

        # LangChain v1 API
        try:
            from langchain.agents import create_agent
        except ImportError:
            create_agent = None

        if create_agent is not None:
            agent = create_agent(
                model=ChatOpenAI(model="gpt-4.1-mini"),
                tools=tools,
                system_prompt=(
                    "You operate a CAW-backed wallet runtime. Always submit a pact before execution, "
                    "wait until it is active, and keep retries inside policy guidance."
                ),
            )
            result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
            print("\nAgent result:", result)
            return

        # Legacy pre-v1 API fallback
        try:
            from langchain.agents import AgentExecutor, create_openai_tools_agent
            from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        except ImportError as exc:
            raise RuntimeError(
                "Unsupported langchain version detected. Install langchain>=1.0.0, "
                "or a compatible legacy release exposing create_openai_tools_agent."
            ) from exc

        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You operate a CAW-backed wallet runtime. Always submit a pact before execution, "
                    "wait until it is active, and keep retries inside policy guidance.",
                ),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        agent = create_openai_tools_agent(llm, tools, prompt_template)
        executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        result = executor.invoke({"input": prompt})
        print("\nAgent result:", result.get("output", result))
    finally:
        asyncio.run(client.close())


if __name__ == "__main__":
    main()

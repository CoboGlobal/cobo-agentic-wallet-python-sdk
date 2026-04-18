"""Canonical Python SDK example for the current CAW onboarding model.

Flow:
1. use an existing paired wallet and API key
2. submit a pact
3. wait until the pact is active
4. execute one compliant transfer
5. trigger one denial and retry with a compliant amount
"""

import asyncio
import os

from cobo_agentic_wallet.client import WalletAPIClient
from cobo_agentic_wallet.errors import PolicyDeniedError

CHAIN_ID = "BASE_ETH"
TOKEN_ID = "USDC"


async def wait_for_active_pact(client: WalletAPIClient, pact_id: str) -> dict:
    while True:
        pact = await client.get_pact(pact_id)
        status = pact.get("status")
        print("pact status:", status)
        if status == "active":
            return pact
        if status in {"rejected", "expired", "revoked", "completed"}:
            raise RuntimeError(f"pact reached terminal status before activation: {status}")
        await asyncio.sleep(5)


async def main() -> None:
    api_url = os.environ["AGENT_WALLET_API_URL"]
    api_key = os.environ["AGENT_WALLET_API_KEY"]
    wallet_id = os.environ["AGENT_WALLET_WALLET_ID"]
    destination = os.environ.get(
        "CAW_DESTINATION",
        "0x1111111111111111111111111111111111111111",
    )

    async with WalletAPIClient(base_url=api_url, api_key=api_key) as client:
        wallets = await client.list_wallets()
        print("wallets:", wallets)

        pact_resp = await client.submit_pact(
            wallet_id=wallet_id,
            intent="Run a controlled transfer example",
            spec={
                "completion_conditions": [
                    {"type": "time_elapsed", "threshold": "86400"}
                ]
            },
        )
        pact_id = pact_resp["pact_id"]
        print("submitted pact:", pact_id)
        print("approve the pact in the Cobo Agentic Wallet app, then wait for activation")

        pact = await wait_for_active_pact(client, pact_id)
        pact_api_key = pact.get("api_key")
        if not pact_api_key:
            raise RuntimeError("active pact did not return a pact-scoped API key")

        async with WalletAPIClient(base_url=api_url, api_key=pact_api_key) as pact_client:
            allowed = await pact_client.transfer_tokens(
                wallet_id,
                chain_id=CHAIN_ID,
                dst_addr=destination,
                token_id=TOKEN_ID,
                amount="50",
                request_id="python-direct-allowed",
            )
            print("allowed transfer:", allowed)

            try:
                await pact_client.transfer_tokens(
                    wallet_id,
                    chain_id=CHAIN_ID,
                    dst_addr=destination,
                    token_id=TOKEN_ID,
                    amount="200",
                    request_id="python-direct-denied",
                )
            except PolicyDeniedError as exc:
                retry_amount = str(exc.denial.details.get("limit_value", "100"))
                print("policy denied:", exc.denial.code)
                print("suggestion:", exc.denial.suggestion)
                retried = await pact_client.transfer_tokens(
                    wallet_id,
                    chain_id=CHAIN_ID,
                    dst_addr=destination,
                    token_id=TOKEN_ID,
                    amount=retry_amount,
                    request_id="python-direct-retry",
                )
                print("retried transfer:", retried)


if __name__ == "__main__":
    asyncio.run(main())

"""Agno toolkit adapter for Cobo Agentic Wallet."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from cobo_agentic_wallet.client import WalletAPIClient
from cobo_agentic_wallet.errors import APIError, PolicyDeniedError
from cobo_agentic_wallet.integrations.agno.tools import build_tool_handler_map, format_denial_text
from cobo_agentic_wallet.toolkit import AgentWalletToolkit

try:
    from agno.tools.toolkit import Toolkit
except ImportError as exc:  # pragma: no cover - import guard
    raise ImportError(
        "agno is required for this integration. Install with: pip install 'cobo-agentic-wallet[agno]'"
    ) from exc


class CoboAgentWalletTools(Toolkit):
    """Agno toolkit exposing Cobo Agentic Wallet tools for use with the Agno agent framework.

    Maps the canonical tool surface from :class:`AgentWalletToolkit` to Agno-compatible
    sync and async methods, and converts policy denials to LLM-readable output so agents
    can self-correct without raising exceptions.
    """

    def __init__(
        self,
        *,
        client: WalletAPIClient,
        name: str = "cobo_agentic_wallet",
        all: bool = False,
        enable_list_wallets: bool = True,
        enable_get_wallet: bool = True,
        enable_list_wallet_addresses: bool = True,
        enable_get_balance: bool = True,
        enable_submit_pact: bool = True,
        enable_get_pact: bool = True,
        enable_list_pacts: bool = True,
        enable_transfer_tokens: bool = True,
        enable_contract_call: bool = True,
        enable_message_sign: bool = True,
        enable_payment: bool = True,
        enable_estimate_transfer_fee: bool = True,
        enable_estimate_contract_call_fee: bool = True,
        enable_list_transactions: bool = True,
        enable_list_transaction_records: bool = True,
        enable_get_transaction_record: bool = True,
        enable_get_transaction_record_by_request_id: bool = True,
        enable_list_recent_addresses: bool = True,
        enable_get_audit_logs: bool = True,
        enable_create_delegation: bool = True,
        include_tools: list[str] | None = None,
        exclude_tools: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        selected_names: list[str] = []

        tools: list[Any] = []
        async_tools: list[tuple[Any, str]] = []
        if all or enable_list_wallets:
            tools.append(self.list_wallets)
            async_tools.append((self.alist_wallets, "list_wallets"))
            selected_names.append("list_wallets")
        if all or enable_get_wallet:
            tools.append(self.get_wallet)
            async_tools.append((self.aget_wallet, "get_wallet"))
            selected_names.append("get_wallet")
        if all or enable_list_wallet_addresses:
            tools.append(self.list_wallet_addresses)
            async_tools.append((self.alist_wallet_addresses, "list_wallet_addresses"))
            selected_names.append("list_wallet_addresses")
        if all or enable_get_balance:
            tools.append(self.get_balance)
            async_tools.append((self.aget_balance, "get_balance"))
            selected_names.append("get_balance")
        if all or enable_submit_pact:
            tools.append(self.submit_pact)
            async_tools.append((self.asubmit_pact, "submit_pact"))
            selected_names.append("submit_pact")
        if all or enable_get_pact:
            tools.append(self.get_pact)
            async_tools.append((self.aget_pact, "get_pact"))
            selected_names.append("get_pact")
        if all or enable_list_pacts:
            tools.append(self.list_pacts)
            async_tools.append((self.alist_pacts, "list_pacts"))
            selected_names.append("list_pacts")
        if all or enable_transfer_tokens:
            tools.append(self.transfer_tokens)
            async_tools.append((self.atransfer_tokens, "transfer_tokens"))
            selected_names.append("transfer_tokens")
        if all or enable_contract_call:
            tools.append(self.contract_call)
            async_tools.append((self.acontract_call, "contract_call"))
            selected_names.append("contract_call")
        if all or enable_message_sign:
            tools.append(self.message_sign)
            async_tools.append((self.amessage_sign, "message_sign"))
            selected_names.append("message_sign")
        if all or enable_payment:
            tools.append(self.payment)
            async_tools.append((self.apayment, "payment"))
            selected_names.append("payment")
        if all or enable_estimate_transfer_fee:
            tools.append(self.estimate_transfer_fee)
            async_tools.append((self.aestimate_transfer_fee, "estimate_transfer_fee"))
            selected_names.append("estimate_transfer_fee")
        if all or enable_estimate_contract_call_fee:
            tools.append(self.estimate_contract_call_fee)
            async_tools.append((self.aestimate_contract_call_fee, "estimate_contract_call_fee"))
            selected_names.append("estimate_contract_call_fee")
        if all or enable_list_transactions:
            tools.append(self.list_transactions)
            async_tools.append((self.alist_transactions, "list_transactions"))
            selected_names.append("list_transactions")
        if all or enable_list_transaction_records:
            tools.append(self.list_transaction_records)
            async_tools.append((self.alist_transaction_records, "list_transaction_records"))
            selected_names.append("list_transaction_records")
        if all or enable_get_transaction_record:
            tools.append(self.get_transaction_record)
            async_tools.append((self.aget_transaction_record, "get_transaction_record"))
            selected_names.append("get_transaction_record")
        if all or enable_get_transaction_record_by_request_id:
            tools.append(self.get_transaction_record_by_request_id)
            async_tools.append(
                (self.aget_transaction_record_by_request_id, "get_transaction_record_by_request_id")
            )
            selected_names.append("get_transaction_record_by_request_id")
        if all or enable_list_recent_addresses:
            tools.append(self.list_recent_addresses)
            async_tools.append((self.alist_recent_addresses, "list_recent_addresses"))
            selected_names.append("list_recent_addresses")
        if all or enable_get_audit_logs:
            tools.append(self.get_audit_logs)
            async_tools.append((self.aget_audit_logs, "get_audit_logs"))
            selected_names.append("get_audit_logs")
        if all or enable_create_delegation:
            tools.append(self.create_delegation)
            async_tools.append((self.acreate_delegation, "create_delegation"))
            selected_names.append("create_delegation")

        # Validate the canonical tool surface on an unfiltered toolkit so adapter
        # drift is caught independently from user-facing include/exclude filtering.
        canonical_toolkit = AgentWalletToolkit(client)
        build_tool_handler_map(canonical_toolkit)

        requested_include = include_tools if include_tools is not None else selected_names
        self._base_toolkit = AgentWalletToolkit(
            client,
            include_tools=requested_include,
            exclude_tools=exclude_tools,
        )
        self._tool_definitions = {tool.name: tool for tool in self._base_toolkit.get_tools()}
        self._handlers = {tool.name: tool.handler for tool in self._base_toolkit.get_tools()}
        allowed_tool_names = set(self._tool_definitions)
        tools = [tool for tool in tools if tool.__name__ in allowed_tool_names]
        async_tools = [item for item in async_tools if item[1] in allowed_tool_names]

        super().__init__(
            name=name,
            tools=tools,
            async_tools=async_tools,
            include_tools=include_tools,
            exclude_tools=exclude_tools,
            **kwargs,
        )
        self._hydrate_tool_metadata()

    def _hydrate_tool_metadata(self) -> None:
        """Copy descriptions and parameter schemas from canonical ToolSpec definitions into registered Agno functions."""

        for registry in (self.functions, self.async_functions):
            for name, function in registry.items():
                definition = self._tool_definitions.get(name)
                if definition is None:
                    continue
                function.description = definition.description
                function.parameters = definition.parameters

    def _error_payload(self, exc: APIError) -> str:
        """Serialize an APIError into a JSON string suitable for raising as a RuntimeError."""
        payload = {
            "error": "API_ERROR",
            "status_code": exc.status_code,
            "message": str(exc),
            "response": exc.response_body,
        }
        return json.dumps(payload, sort_keys=True)

    async def _invoke_async(self, tool_name: str, **kwargs: Any) -> Any:
        """Dispatch an async tool call, converting policy denials to readable text and API errors to RuntimeError."""
        try:
            return await self._handlers[tool_name](**kwargs)
        except PolicyDeniedError as exc:
            return format_denial_text(self._base_toolkit, exc.denial)
        except APIError as exc:
            raise RuntimeError(self._error_payload(exc)) from exc

    def _invoke_sync(self, tool_name: str, **kwargs: Any) -> Any:
        """Run _invoke_async in a new event loop; raises RuntimeError if called from within a running loop."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self._invoke_async(tool_name, **kwargs))

        raise RuntimeError(
            "CoboAgentWalletTools are synchronous wrappers over async API calls. "
            "Call them from a sync context, or run them in a separate thread from async code."
        )

    def list_wallets(self, limit: int = 50, offset: int = 0, include_archived: bool = False) -> Any:
        """List wallets accessible to the caller."""

        return self._invoke_sync(
            "list_wallets",
            limit=limit,
            offset=offset,
            include_archived=include_archived,
        )

    def get_wallet(self, wallet_uuid: str, include_spend_summary: bool = False) -> Any:
        """Get wallet metadata and status."""

        return self._invoke_sync(
            "get_wallet",
            wallet_uuid=wallet_uuid,
            include_spend_summary=include_spend_summary,
        )

    def list_wallet_addresses(self, wallet_uuid: str) -> Any:
        """List on-chain addresses belonging to a wallet."""

        return self._invoke_sync("list_wallet_addresses", wallet_uuid=wallet_uuid)

    def get_balance(self, wallet_uuid: str) -> Any:
        """Get wallet balances for a specific wallet."""

        return self._invoke_sync("get_balance", wallet_uuid=wallet_uuid)

    def submit_pact(
        self,
        wallet_id: str,
        intent: str,
        spec: dict[str, Any],
        original_intent: str | None = None,
        name: str | None = None,
    ) -> Any:
        """Submit a pact for owner approval."""

        return self._invoke_sync(
            "submit_pact",
            wallet_id=wallet_id,
            intent=intent,
            spec=spec,
            original_intent=original_intent,
            name=name,
        )

    def get_pact(self, pact_id: str) -> Any:
        """Get pact details and status."""

        return self._invoke_sync("get_pact", pact_id=pact_id)

    def list_pacts(
        self,
        status: str | None = None,
        wallet_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Any:
        """List pacts visible to the caller."""

        return self._invoke_sync(
            "list_pacts",
            status=status,
            wallet_id=wallet_id,
            limit=limit,
            offset=offset,
        )

    def transfer_tokens(
        self,
        wallet_uuid: str,
        dst_addr: str,
        token_id: str,
        amount: str,
        chain_id: str = "ETH",
        request_id: str | None = None,
        fee: dict[str, Any] | None = None,
    ) -> Any:
        """Transfer tokens to a destination address with policy enforcement."""

        return self._invoke_sync(
            "transfer_tokens",
            wallet_uuid=wallet_uuid,
            chain_id=chain_id,
            dst_addr=dst_addr,
            token_id=token_id,
            amount=amount,
            request_id=request_id,
            fee=fee,
        )

    def contract_call(
        self,
        wallet_uuid: str,
        chain_id: str,
        contract_addr: str | None = None,
        value: str = "0",
        calldata: str | None = None,
        instructions: list[dict[str, Any]] | None = None,
        address_lookup_table_accounts: list[dict[str, Any]] | None = None,
        request_id: str | None = None,
        fee: dict[str, Any] | None = None,
        src_addr: str | None = None,
        sponsor: bool | None = None,
        gas_provider: str | None = None,
        description: str | None = None,
    ) -> Any:
        """Call a smart contract from the wallet."""

        return self._invoke_sync(
            "contract_call",
            wallet_uuid=wallet_uuid,
            chain_id=chain_id,
            contract_addr=contract_addr,
            value=value,
            calldata=calldata,
            instructions=instructions,
            address_lookup_table_accounts=address_lookup_table_accounts,
            request_id=request_id,
            fee=fee,
            src_addr=src_addr,
            sponsor=sponsor,
            gas_provider=gas_provider,
            description=description,
        )

    def message_sign(
        self,
        wallet_uuid: str,
        chain_id: str,
        destination_type: str | None = None,
        eip712_typed_data: dict[str, Any] | None = None,
        source_address: str | None = None,
        description: str | None = None,
        sync: bool = True,
        request_id: str | None = None,
    ) -> Any:
        """Sign a message or typed data with the wallet."""

        return self._invoke_sync(
            "message_sign",
            wallet_uuid=wallet_uuid,
            chain_id=chain_id,
            destination_type=destination_type,
            eip712_typed_data=eip712_typed_data,
            source_address=source_address,
            description=description,
            sync=sync,
            request_id=request_id,
        )

    def payment(
        self,
        wallet_uuid: str,
        protocol: str,
        request_id: str | None = None,
        x402_payment_required: str | None = None,
        mpp_www_authenticate: str | None = None,
        mpp_session: dict[str, Any] | None = None,
    ) -> Any:
        """Submit an x402 or MPP payment request."""

        return self._invoke_sync(
            "payment",
            wallet_uuid=wallet_uuid,
            protocol=protocol,
            request_id=request_id,
            x402_payment_required=x402_payment_required,
            mpp_www_authenticate=mpp_www_authenticate,
            mpp_session=mpp_session,
        )

    def estimate_transfer_fee(
        self,
        wallet_uuid: str,
        dst_addr: str,
        amount: str,
        token_id: str | None = None,
        chain_id: str | None = None,
        src_addr: str | None = None,
    ) -> Any:
        """Estimate the fee for a token transfer."""

        return self._invoke_sync(
            "estimate_transfer_fee",
            wallet_uuid=wallet_uuid,
            dst_addr=dst_addr,
            amount=amount,
            token_id=token_id,
            chain_id=chain_id,
            src_addr=src_addr,
        )

    def estimate_contract_call_fee(
        self,
        wallet_uuid: str,
        chain_id: str,
        contract_addr: str | None = None,
        value: str = "0",
        calldata: str | None = None,
        instructions: list[dict[str, Any]] | None = None,
        address_lookup_table_accounts: list[dict[str, Any]] | None = None,
        src_addr: str | None = None,
    ) -> Any:
        """Estimate the fee for a contract call."""

        return self._invoke_sync(
            "estimate_contract_call_fee",
            wallet_uuid=wallet_uuid,
            chain_id=chain_id,
            contract_addr=contract_addr,
            value=value,
            calldata=calldata,
            instructions=instructions,
            address_lookup_table_accounts=address_lookup_table_accounts,
            src_addr=src_addr,
        )

    def list_transactions(
        self,
        wallet_uuid: str,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
    ) -> Any:
        """List transactions for a wallet with optional status filter."""

        return self._invoke_sync(
            "list_transactions",
            wallet_uuid=wallet_uuid,
            limit=limit,
            offset=offset,
            status=status,
        )

    def list_transaction_records(
        self,
        wallet_uuid: str,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        record_type: str | None = None,
        token_id: str | None = None,
        chain_id: str | None = None,
        address_id: str | None = None,
    ) -> Any:
        """List persisted transaction records for a wallet."""

        return self._invoke_sync(
            "list_transaction_records",
            wallet_uuid=wallet_uuid,
            limit=limit,
            offset=offset,
            status=status,
            record_type=record_type,
            token_id=token_id,
            chain_id=chain_id,
            address_id=address_id,
        )

    def get_transaction_record(self, wallet_uuid: str, record_uuid: str) -> Any:
        """Get a transaction record by record UUID."""

        return self._invoke_sync(
            "get_transaction_record",
            wallet_uuid=wallet_uuid,
            record_uuid=record_uuid,
        )

    def get_transaction_record_by_request_id(self, wallet_uuid: str, request_id: str) -> Any:
        """Look up a transaction record by idempotency request ID."""

        return self._invoke_sync(
            "get_transaction_record_by_request_id",
            wallet_uuid=wallet_uuid,
            request_id=request_id,
        )

    def list_recent_addresses(self, wallet_uuid: str, limit: int = 20) -> Any:
        """List recently used destination addresses."""

        return self._invoke_sync(
            "list_recent_addresses",
            wallet_uuid=wallet_uuid,
            limit=limit,
        )

    def get_audit_logs(
        self,
        wallet_id: str | None = None,
        principal_id: str | None = None,
        action: str | None = None,
        result: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> Any:
        """Query audit logs with filters and cursor pagination."""

        return self._invoke_sync(
            "get_audit_logs",
            wallet_id=wallet_id,
            principal_id=principal_id,
            action=action,
            result=result,
            start_time=start_time,
            end_time=end_time,
            cursor=cursor,
            limit=limit,
        )

    def create_delegation(
        self,
        operator_id: str,
        wallet_id: str,
        permissions: list[str],
        policies: list[dict[str, Any]] | None = None,
        constraints: dict[str, Any] | None = None,
        expires_at: str | None = None,
    ) -> Any:
        """Create delegation granting an operator scoped wallet permissions."""

        return self._invoke_sync(
            "create_delegation",
            operator_id=operator_id,
            wallet_id=wallet_id,
            permissions=permissions,
            policies=policies,
            constraints=constraints,
            expires_at=expires_at,
        )

    async def alist_wallets(
        self, limit: int = 50, offset: int = 0, include_archived: bool = False
    ) -> Any:
        """List wallets accessible to the caller."""

        return await self._invoke_async(
            "list_wallets",
            limit=limit,
            offset=offset,
            include_archived=include_archived,
        )

    async def aget_wallet(self, wallet_uuid: str, include_spend_summary: bool = False) -> Any:
        """Get wallet metadata and status."""

        return await self._invoke_async(
            "get_wallet",
            wallet_uuid=wallet_uuid,
            include_spend_summary=include_spend_summary,
        )

    async def alist_wallet_addresses(self, wallet_uuid: str) -> Any:
        """List on-chain addresses belonging to a wallet."""

        return await self._invoke_async("list_wallet_addresses", wallet_uuid=wallet_uuid)

    async def aget_balance(self, wallet_uuid: str) -> Any:
        """Get wallet balances for a specific wallet."""

        return await self._invoke_async("get_balance", wallet_uuid=wallet_uuid)

    async def asubmit_pact(
        self,
        wallet_id: str,
        intent: str,
        spec: dict[str, Any],
        original_intent: str | None = None,
        name: str | None = None,
    ) -> Any:
        """Submit a pact for owner approval."""

        return await self._invoke_async(
            "submit_pact",
            wallet_id=wallet_id,
            intent=intent,
            spec=spec,
            original_intent=original_intent,
            name=name,
        )

    async def aget_pact(self, pact_id: str) -> Any:
        """Get pact details and status."""

        return await self._invoke_async("get_pact", pact_id=pact_id)

    async def alist_pacts(
        self,
        status: str | None = None,
        wallet_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Any:
        """List pacts visible to the caller."""

        return await self._invoke_async(
            "list_pacts",
            status=status,
            wallet_id=wallet_id,
            limit=limit,
            offset=offset,
        )

    async def atransfer_tokens(
        self,
        wallet_uuid: str,
        dst_addr: str,
        token_id: str,
        amount: str,
        chain_id: str = "ETH",
        request_id: str | None = None,
        fee: dict[str, Any] | None = None,
    ) -> Any:
        """Transfer tokens to a destination address with policy enforcement."""

        return await self._invoke_async(
            "transfer_tokens",
            wallet_uuid=wallet_uuid,
            chain_id=chain_id,
            dst_addr=dst_addr,
            token_id=token_id,
            amount=amount,
            request_id=request_id,
            fee=fee,
        )

    async def acontract_call(
        self,
        wallet_uuid: str,
        chain_id: str,
        contract_addr: str | None = None,
        value: str = "0",
        calldata: str | None = None,
        instructions: list[dict[str, Any]] | None = None,
        address_lookup_table_accounts: list[dict[str, Any]] | None = None,
        request_id: str | None = None,
        fee: dict[str, Any] | None = None,
        src_addr: str | None = None,
        sponsor: bool | None = None,
        gas_provider: str | None = None,
        description: str | None = None,
    ) -> Any:
        """Call a smart contract from the wallet."""

        return await self._invoke_async(
            "contract_call",
            wallet_uuid=wallet_uuid,
            chain_id=chain_id,
            contract_addr=contract_addr,
            value=value,
            calldata=calldata,
            instructions=instructions,
            address_lookup_table_accounts=address_lookup_table_accounts,
            request_id=request_id,
            fee=fee,
            src_addr=src_addr,
            sponsor=sponsor,
            gas_provider=gas_provider,
            description=description,
        )

    async def amessage_sign(
        self,
        wallet_uuid: str,
        chain_id: str,
        destination_type: str | None = None,
        eip712_typed_data: dict[str, Any] | None = None,
        source_address: str | None = None,
        description: str | None = None,
        sync: bool = True,
        request_id: str | None = None,
    ) -> Any:
        """Sign a message or typed data with the wallet."""

        return await self._invoke_async(
            "message_sign",
            wallet_uuid=wallet_uuid,
            chain_id=chain_id,
            destination_type=destination_type,
            eip712_typed_data=eip712_typed_data,
            source_address=source_address,
            description=description,
            sync=sync,
            request_id=request_id,
        )

    async def apayment(
        self,
        wallet_uuid: str,
        protocol: str,
        request_id: str | None = None,
        x402_payment_required: str | None = None,
        mpp_www_authenticate: str | None = None,
        mpp_session: dict[str, Any] | None = None,
    ) -> Any:
        """Submit an x402 or MPP payment request."""

        return await self._invoke_async(
            "payment",
            wallet_uuid=wallet_uuid,
            protocol=protocol,
            request_id=request_id,
            x402_payment_required=x402_payment_required,
            mpp_www_authenticate=mpp_www_authenticate,
            mpp_session=mpp_session,
        )

    async def aestimate_transfer_fee(
        self,
        wallet_uuid: str,
        dst_addr: str,
        amount: str,
        token_id: str | None = None,
        chain_id: str | None = None,
        src_addr: str | None = None,
    ) -> Any:
        """Estimate the fee for a token transfer."""

        return await self._invoke_async(
            "estimate_transfer_fee",
            wallet_uuid=wallet_uuid,
            dst_addr=dst_addr,
            amount=amount,
            token_id=token_id,
            chain_id=chain_id,
            src_addr=src_addr,
        )

    async def aestimate_contract_call_fee(
        self,
        wallet_uuid: str,
        chain_id: str,
        contract_addr: str | None = None,
        value: str = "0",
        calldata: str | None = None,
        instructions: list[dict[str, Any]] | None = None,
        address_lookup_table_accounts: list[dict[str, Any]] | None = None,
        src_addr: str | None = None,
    ) -> Any:
        """Estimate the fee for a contract call."""

        return await self._invoke_async(
            "estimate_contract_call_fee",
            wallet_uuid=wallet_uuid,
            chain_id=chain_id,
            contract_addr=contract_addr,
            value=value,
            calldata=calldata,
            instructions=instructions,
            address_lookup_table_accounts=address_lookup_table_accounts,
            src_addr=src_addr,
        )

    async def alist_transactions(
        self,
        wallet_uuid: str,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
    ) -> Any:
        """List transactions for a wallet with optional status filter."""

        return await self._invoke_async(
            "list_transactions",
            wallet_uuid=wallet_uuid,
            limit=limit,
            offset=offset,
            status=status,
        )

    async def alist_transaction_records(
        self,
        wallet_uuid: str,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        record_type: str | None = None,
        token_id: str | None = None,
        chain_id: str | None = None,
        address_id: str | None = None,
    ) -> Any:
        """List persisted transaction records for a wallet."""

        return await self._invoke_async(
            "list_transaction_records",
            wallet_uuid=wallet_uuid,
            limit=limit,
            offset=offset,
            status=status,
            record_type=record_type,
            token_id=token_id,
            chain_id=chain_id,
            address_id=address_id,
        )

    async def aget_transaction_record(self, wallet_uuid: str, record_uuid: str) -> Any:
        """Get a transaction record by record UUID."""

        return await self._invoke_async(
            "get_transaction_record",
            wallet_uuid=wallet_uuid,
            record_uuid=record_uuid,
        )

    async def aget_transaction_record_by_request_id(self, wallet_uuid: str, request_id: str) -> Any:
        """Look up a transaction record by idempotency request ID."""

        return await self._invoke_async(
            "get_transaction_record_by_request_id",
            wallet_uuid=wallet_uuid,
            request_id=request_id,
        )

    async def alist_recent_addresses(self, wallet_uuid: str, limit: int = 20) -> Any:
        """List recently used destination addresses."""

        return await self._invoke_async(
            "list_recent_addresses",
            wallet_uuid=wallet_uuid,
            limit=limit,
        )

    async def aget_audit_logs(
        self,
        wallet_id: str | None = None,
        principal_id: str | None = None,
        action: str | None = None,
        result: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> Any:
        """Query audit logs with filters and cursor pagination."""

        return await self._invoke_async(
            "get_audit_logs",
            wallet_id=wallet_id,
            principal_id=principal_id,
            action=action,
            result=result,
            start_time=start_time,
            end_time=end_time,
            cursor=cursor,
            limit=limit,
        )

    async def acreate_delegation(
        self,
        operator_id: str,
        wallet_id: str,
        permissions: list[str],
        policies: list[dict[str, Any]] | None = None,
        constraints: dict[str, Any] | None = None,
        expires_at: str | None = None,
    ) -> Any:
        """Create delegation granting an operator scoped wallet permissions."""

        return await self._invoke_async(
            "create_delegation",
            operator_id=operator_id,
            wallet_id=wallet_id,
            permissions=permissions,
            policies=policies,
            constraints=constraints,
            expires_at=expires_at,
        )


# Backward compatibility with earlier naming used during P8 scaffolding.
CoboAgentWalletToolkit = CoboAgentWalletTools

__all__ = ["CoboAgentWalletTools", "CoboAgentWalletToolkit"]

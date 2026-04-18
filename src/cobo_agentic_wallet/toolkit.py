"""Agent toolkit base abstractions for Cobo Agentic Wallet integrations."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from cobo_agentic_wallet.errors import PolicyDenial
from cobo_agentic_wallet.tool_specs import get_tool_spec
from cobo_agentic_wallet_api.models.delegation_permission import DelegationPermission
from cobo_agentic_wallet_api.models.inline_policy_create import InlinePolicyCreate
from cobo_agentic_wallet_api.models.policy_type import PolicyType

ToolHandler = Callable[..., Awaitable[Any]]


@dataclass(frozen=True)
class ToolDefinition:
    """Framework-agnostic tool descriptor."""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler


class AgentWalletToolkit:
    """Framework-agnostic adapter layer for exposing wallet APIs as agent tools.

    Framework-specific integrations (MCP, LangChain, OpenAI, Agno, etc.)
    consume these ``ToolDefinition`` objects and control how errors are surfaced
    to their respective runtimes.
    """

    def __init__(
        self,
        client: Any,
        *,
        include_tools: list[str] | None = None,
        exclude_tools: list[str] | None = None,
    ) -> None:
        self._client = client
        self._include_tools = tuple(include_tools) if include_tools is not None else None
        self._exclude_tools = set(exclude_tools or [])

    @property
    def client(self) -> Any:
        """Return the underlying API client."""
        return self._client

    @property
    def include_tools(self) -> tuple[str, ...] | None:
        """Return the optional allowlist of tool names configured for this toolkit."""

        return self._include_tools

    @property
    def exclude_tools(self) -> set[str]:
        """Return the denylist of tool names configured for this toolkit."""

        return set(self._exclude_tools)

    def get_tools(self) -> list[ToolDefinition]:
        """Return the canonical tool set for framework adapters."""
        tools = [
            self._list_wallets_tool(),
            self._get_wallet_tool(),
            self._list_wallet_addresses_tool(),
            self._get_balance_tool(),
            self._submit_pact_tool(),
            self._get_pact_tool(),
            self._list_pacts_tool(),
            self._transfer_tokens_tool(),
            self._contract_call_tool(),
            self._message_sign_tool(),
            self._payment_tool(),
            self._estimate_transfer_fee_tool(),
            self._estimate_contract_call_fee_tool(),
            self._list_transactions_tool(),
            self._list_transaction_records_tool(),
            self._get_transaction_record_tool(),
            self._get_transaction_record_by_request_id_tool(),
            self._list_recent_addresses_tool(),
            self._get_audit_logs_tool(),
            self._create_delegation_tool(),
        ]
        return self._select_tools(
            tools,
            include_tools=self._include_tools,
            exclude_tools=self._exclude_tools,
        )

    @staticmethod
    def _select_tools(
        tools: list[ToolDefinition],
        *,
        include_tools: tuple[str, ...] | None,
        exclude_tools: set[str],
    ) -> list[ToolDefinition]:
        """Filter tool definitions using optional include/exclude name lists."""

        by_name = {tool.name: tool for tool in tools}
        available_names = set(by_name)

        requested_names = available_names if include_tools is None else set(include_tools)
        unknown_names = (requested_names | exclude_tools) - available_names
        if unknown_names:
            unknown_joined = ", ".join(sorted(unknown_names))
            raise ValueError(f"Unknown tool names requested: {unknown_joined}")

        selected_names = requested_names - exclude_tools
        if include_tools is None:
            ordered_names = [tool.name for tool in tools if tool.name in selected_names]
        else:
            ordered_names = [name for name in include_tools if name in selected_names]

        return [by_name[name] for name in ordered_names]

    def _list_wallets_tool(self) -> ToolDefinition:
        """Build the list_wallets ToolDefinition."""

        async def list_wallets(
            *, limit: int = 50, offset: int = 0, include_archived: bool = False
        ) -> Any:
            return await self._client.list_wallets(
                limit=limit,
                offset=offset,
                include_archived=include_archived,
            )

        return self._build_tool_definition("list_wallets", list_wallets)

    def _get_wallet_tool(self) -> ToolDefinition:
        """Build the get_wallet ToolDefinition."""

        async def get_wallet(*, wallet_uuid: str, include_spend_summary: bool = False) -> Any:
            return await self._client.get_wallet(
                wallet_uuid,
                include_spend_summary=include_spend_summary,
            )

        return self._build_tool_definition("get_wallet", get_wallet)

    def _list_wallet_addresses_tool(self) -> ToolDefinition:
        """Build the list_wallet_addresses ToolDefinition."""

        async def list_wallet_addresses(*, wallet_uuid: str) -> Any:
            return await self._client.list_wallet_addresses(wallet_uuid)

        return self._build_tool_definition("list_wallet_addresses", list_wallet_addresses)

    def _get_balance_tool(self) -> ToolDefinition:
        """Build the get_balance ToolDefinition."""

        async def get_balance(
            *,
            wallet_uuid: str,
            chain_id: str | None = None,
            token_id: str | None = None,
            force_refresh: bool = False,
        ) -> Any:
            return await self._client.list_balances(
                wallet_uuid=wallet_uuid,
                chain_id=chain_id,
                token_id=token_id,
                force_refresh=force_refresh,
            )

        return self._build_tool_definition("get_balance", get_balance)

    def _submit_pact_tool(self) -> ToolDefinition:
        """Build the submit_pact ToolDefinition."""

        async def submit_pact(
            *,
            wallet_id: str,
            intent: str,
            spec: dict[str, Any],
            original_intent: str | None = None,
            name: str | None = None,
        ) -> Any:
            return await self._client.submit_pact(
                wallet_id=wallet_id,
                intent=intent,
                original_intent=original_intent,
                spec=spec,
                name=name,
            )

        return self._build_tool_definition("submit_pact", submit_pact)

    def _get_pact_tool(self) -> ToolDefinition:
        """Build the get_pact ToolDefinition."""

        async def get_pact(*, pact_id: str) -> Any:
            return await self._client.get_pact(pact_id)

        return self._build_tool_definition("get_pact", get_pact)

    def _list_pacts_tool(self) -> ToolDefinition:
        """Build the list_pacts ToolDefinition."""

        async def list_pacts(
            *,
            status: str | None = None,
            wallet_id: str | None = None,
            limit: int = 50,
            offset: int = 0,
        ) -> Any:
            return await self._client.list_pacts(
                status=status,
                wallet_id=wallet_id,
                limit=limit,
                offset=offset,
            )

        return self._build_tool_definition("list_pacts", list_pacts)

    def _transfer_tokens_tool(self) -> ToolDefinition:
        """Build the transfer_tokens ToolDefinition."""

        async def transfer_tokens(
            *,
            wallet_uuid: str,
            dst_addr: str,
            token_id: str,
            amount: str,
            chain_id: str,
            request_id: str | None = None,
            fee: dict[str, Any] | None = None,
        ) -> Any:
            _ = fee  # Reserved for future use
            return await self._client.transfer_tokens(
                wallet_uuid,
                chain_id=chain_id,
                dst_addr=dst_addr,
                token_id=token_id,
                amount=amount,
                request_id=request_id,
            )

        return self._build_tool_definition("transfer_tokens", transfer_tokens)

    def _contract_call_tool(self) -> ToolDefinition:
        """Build the contract_call ToolDefinition."""

        async def contract_call(
            *,
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
            return await self._client.contract_call(
                wallet_uuid,
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

        return self._build_tool_definition("contract_call", contract_call)

    def _message_sign_tool(self) -> ToolDefinition:
        """Build the message_sign ToolDefinition."""

        async def message_sign(
            *,
            wallet_uuid: str,
            chain_id: str,
            destination_type: str | None = None,
            eip712_typed_data: dict[str, Any] | None = None,
            source_address: str | None = None,
            description: str | None = None,
            sync: bool = True,
            request_id: str | None = None,
        ) -> Any:
            return await self._client.message_sign(
                wallet_uuid,
                chain_id=chain_id,
                destination_type=destination_type,
                eip712_typed_data=eip712_typed_data,
                source_address=source_address,
                description=description,
                sync=sync,
                request_id=request_id,
            )

        return self._build_tool_definition("message_sign", message_sign)

    def _payment_tool(self) -> ToolDefinition:
        """Build the payment ToolDefinition."""

        async def payment(
            *,
            wallet_uuid: str,
            protocol: str,
            request_id: str | None = None,
            x402_payment_required: str | None = None,
            mpp_www_authenticate: str | None = None,
            mpp_session: dict[str, Any] | None = None,
        ) -> Any:
            return await self._client.payment(
                wallet_uuid,
                protocol=protocol,
                request_id=request_id,
                x402_payment_required=x402_payment_required,
                mpp_www_authenticate=mpp_www_authenticate,
                mpp_session=mpp_session,
            )

        return self._build_tool_definition("payment", payment)

    def _estimate_transfer_fee_tool(self) -> ToolDefinition:
        """Build the estimate_transfer_fee ToolDefinition."""

        async def estimate_transfer_fee(
            *,
            wallet_uuid: str,
            dst_addr: str,
            amount: str,
            token_id: str | None = None,
            chain_id: str | None = None,
            src_addr: str | None = None,
        ) -> Any:
            return await self._client.estimate_transfer_fee(
                wallet_uuid,
                dst_addr=dst_addr,
                amount=amount,
                token_id=token_id,
                chain_id=chain_id,
                src_addr=src_addr,
            )

        return self._build_tool_definition("estimate_transfer_fee", estimate_transfer_fee)

    def _estimate_contract_call_fee_tool(self) -> ToolDefinition:
        """Build the estimate_contract_call_fee ToolDefinition."""

        async def estimate_contract_call_fee(
            *,
            wallet_uuid: str,
            chain_id: str,
            contract_addr: str | None = None,
            value: str = "0",
            calldata: str | None = None,
            instructions: list[dict[str, Any]] | None = None,
            address_lookup_table_accounts: list[dict[str, Any]] | None = None,
            src_addr: str | None = None,
        ) -> Any:
            return await self._client.estimate_contract_call_fee(
                wallet_uuid,
                chain_id=chain_id,
                contract_addr=contract_addr,
                value=value,
                calldata=calldata,
                instructions=instructions,
                address_lookup_table_accounts=address_lookup_table_accounts,
                src_addr=src_addr,
            )

        return self._build_tool_definition(
            "estimate_contract_call_fee",
            estimate_contract_call_fee,
        )

    def _list_transactions_tool(self) -> ToolDefinition:
        """Build the list_transactions ToolDefinition."""

        async def list_transactions(
            *,
            wallet_uuid: str,
            limit: int = 50,
            offset: int = 0,
            status: str | None = None,
        ) -> Any:
            return await self._client.list_transactions(
                wallet_uuid,
                limit=limit,
                offset=offset,
                status=status,
            )

        return self._build_tool_definition("list_transactions", list_transactions)

    def _list_transaction_records_tool(self) -> ToolDefinition:
        """Build the list_transaction_records ToolDefinition."""

        async def list_transaction_records(
            *,
            wallet_uuid: str,
            limit: int = 50,
            offset: int = 0,
            status: str | None = None,
            record_type: str | None = None,
            token_id: str | None = None,
            chain_id: str | None = None,
            address_id: str | None = None,
        ) -> Any:
            return await self._client.list_transaction_records(
                wallet_uuid=wallet_uuid,
                limit=limit,
                offset=offset,
                status=status,
                record_type=record_type,
                token_id=token_id,
                chain_id=chain_id,
                address_id=address_id,
            )

        return self._build_tool_definition("list_transaction_records", list_transaction_records)

    def _get_transaction_record_tool(self) -> ToolDefinition:
        """Build the get_transaction_record ToolDefinition."""

        async def get_transaction_record(*, wallet_uuid: str, record_uuid: str) -> Any:
            return await self._client.get_transaction_record(wallet_uuid, record_uuid)

        return self._build_tool_definition("get_transaction_record", get_transaction_record)

    def _get_transaction_record_by_request_id_tool(self) -> ToolDefinition:
        """Build the get_transaction_record_by_request_id ToolDefinition."""

        async def get_transaction_record_by_request_id(
            *,
            wallet_uuid: str,
            request_id: str,
        ) -> Any:
            return await self._client.get_transaction_record_by_request_id(wallet_uuid, request_id)

        return self._build_tool_definition(
            "get_transaction_record_by_request_id",
            get_transaction_record_by_request_id,
        )

    def _list_recent_addresses_tool(self) -> ToolDefinition:
        """Build the list_recent_addresses ToolDefinition."""

        async def list_recent_addresses(*, wallet_uuid: str, limit: int = 20) -> Any:
            return await self._client.list_recent_addresses(wallet_uuid, limit=limit)

        return self._build_tool_definition("list_recent_addresses", list_recent_addresses)

    def _get_audit_logs_tool(self) -> ToolDefinition:
        """Build the get_audit_logs ToolDefinition."""

        async def get_audit_logs(
            *,
            wallet_id: str | None = None,
            principal_id: str | None = None,
            action: str | None = None,
            result: str | None = None,
            start_time: str | None = None,
            end_time: str | None = None,
            cursor: str | None = None,
            limit: int = 50,
        ) -> Any:
            return await self._client.list_audit_logs(
                wallet_id=wallet_id,
                principal_id=principal_id,
                action=action,
                result=result,
                start_time=start_time,
                end_time=end_time,
                cursor=cursor,
                limit=limit,
            )

        return self._build_tool_definition("get_audit_logs", get_audit_logs)

    def _create_delegation_tool(self) -> ToolDefinition:
        """Build the create_delegation ToolDefinition."""

        async def create_delegation(
            *,
            operator_id: str,
            wallet_id: str,
            permissions: list[str],
            policies: list[dict[str, Any]] | None = None,
            constraints: dict[str, Any] | None = None,
            expires_at: str | None = None,
        ) -> Any:
            # Convert string permissions to enum
            permissions_enum = [DelegationPermission(p) for p in permissions]
            # Build inline policies from both policies and constraints
            inline_policies: list[InlinePolicyCreate] = []
            if policies:
                for p in policies:
                    inline_policies.append(
                        InlinePolicyCreate(
                            name=p.get("name", "policy"),
                            type=PolicyType(p.get("type", "transfer")),
                            rules=p.get("rules", {}),
                        )
                    )
            if constraints:
                # Convert legacy constraints to inline policy
                inline_policies.append(
                    InlinePolicyCreate(
                        name="legacy-constraints",
                        type=PolicyType.TRANSFER,
                        rules=constraints,
                    )
                )
            return await self._client.create_delegation(
                operator_id=operator_id,
                wallet_id=wallet_id,
                permissions=permissions_enum,
                policies=inline_policies if inline_policies else None,
                expires_at=expires_at,
            )

        return self._build_tool_definition("create_delegation", create_delegation)

    @staticmethod
    def _build_tool_definition(name: str, handler: ToolHandler) -> ToolDefinition:
        """Combine a named ToolSpec with its async handler into a ToolDefinition."""
        spec = get_tool_spec(name)
        return ToolDefinition(
            name=spec.name,
            description=spec.description,
            parameters=copy.deepcopy(spec.parameters),
            handler=handler,
        )

    @staticmethod
    def _format_denial(error: PolicyDenial) -> str:
        """Format a policy denial into an LLM-readable guidance message."""

        lines = [f"Policy Denied [{error.code}]: {error.reason}"]
        for key, value in sorted(error.details.items()):
            lines.append(f"  {key}: {value}")
        if error.suggestion:
            lines.append(f"Suggestion: {error.suggestion}")
        return "\n".join(lines)

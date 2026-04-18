"""Transaction operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

from cobo_agentic_wallet_api.models.contract_call_create import ContractCallCreate
from cobo_agentic_wallet_api.models.drop_transaction_request import DropTransactionRequest
from cobo_agentic_wallet_api.models.estimate_contract_call_fee_request import (
    EstimateContractCallFeeRequest,
)
from cobo_agentic_wallet_api.models.estimate_transfer_fee_request import EstimateTransferFeeRequest
from cobo_agentic_wallet_api.models.message_sign_create import MessageSignCreate
from cobo_agentic_wallet_api.models.payment_create import PaymentCreate
from cobo_agentic_wallet_api.models.speedup_transaction_request import SpeedupTransactionRequest
from cobo_agentic_wallet_api.models.transfer_create import TransferCreate

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class TransactionMixin:
    """Transaction operations mixin (auto-generated)."""

    _extract_result: Any
    _transactions_api: Any

    async def contract_call(
        self: "BaseClient",
        wallet_uuid: str,
        *,
        chain_id: str = None,
        contract_addr: str | None = None,
        value: str | None = "0",
        calldata: str | None = None,
        instructions: list[Any] | None = None,
        address_lookup_table_accounts: list[Any] | None = None,
        request_id: str | None = None,
        fee: Any | None = None,
        src_addr: str | None = None,
        sponsor: bool | None = None,
        gas_provider: str | None = None,
        description: str | None = None,
    ) -> Any:
        """Call contract"""
        contract_call_create = ContractCallCreate(
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
        response = await self._transactions_api.contract_call(wallet_uuid, contract_call_create)
        return self._extract_result(response)

    async def drop_transaction(
        self: "BaseClient",
        wallet_uuid: str,
        transaction_uuid: str,
        *,
        request_id: str | None = None,
        fee: Any | None = None,
        cobo_transaction_id: str | None = None,
    ) -> Any:
        """Drop transaction"""
        drop_transaction_request = DropTransactionRequest(
            request_id=request_id, fee=fee, cobo_transaction_id=cobo_transaction_id
        )
        response = await self._transactions_api.drop_transaction(
            wallet_uuid, transaction_uuid, drop_transaction_request
        )
        return self._extract_result(response)

    async def estimate_contract_call_fee(
        self: "BaseClient",
        wallet_uuid: str,
        *,
        chain_id: str = None,
        contract_addr: str | None = None,
        value: str | None = "0",
        calldata: str | None = None,
        instructions: list[Any] | None = None,
        address_lookup_table_accounts: list[Any] | None = None,
        src_addr: str | None = None,
    ) -> Any:
        """Estimate contract call fee"""
        estimate_contract_call_fee_request = EstimateContractCallFeeRequest(
            chain_id=chain_id,
            contract_addr=contract_addr,
            value=value,
            calldata=calldata,
            instructions=instructions,
            address_lookup_table_accounts=address_lookup_table_accounts,
            src_addr=src_addr,
        )
        response = await self._transactions_api.estimate_contract_call_fee(
            wallet_uuid, estimate_contract_call_fee_request
        )
        return self._extract_result(response)

    async def estimate_transfer_fee(
        self: "BaseClient",
        wallet_uuid: str,
        *,
        dst_addr: str = None,
        amount: str = None,
        token_id: str | None = "SETH",
        chain_id: str | None = None,
        src_addr: str | None = None,
    ) -> Any:
        """Estimate transfer fee"""
        estimate_transfer_fee_request = EstimateTransferFeeRequest(
            dst_addr=dst_addr,
            amount=amount,
            token_id=token_id,
            chain_id=chain_id,
            src_addr=src_addr,
        )
        response = await self._transactions_api.estimate_transfer_fee(
            wallet_uuid, estimate_transfer_fee_request
        )
        return self._extract_result(response)

    async def handle_waas_webhook(
        self: "BaseClient",
        body: dict[str, Any],
        biz_timestamp: str | None = None,
        biz_resp_signature: str | None = None,
    ) -> Any:
        """Handle WaaS webhook"""
        response = await self._transactions_api.handle_waas_webhook(
            body, biz_timestamp, biz_resp_signature
        )
        return self._extract_result(response)

    async def list_recent_addresses(
        self: "BaseClient", wallet_uuid: str, limit: int | None = None
    ) -> Any:
        """List recent addresses"""
        response = await self._transactions_api.list_recent_addresses(wallet_uuid, limit)
        return self._extract_result(response)

    async def message_sign(
        self: "BaseClient",
        wallet_uuid: str,
        *,
        chain_id: str = None,
        destination_type: Any | None = None,
        eip712_typed_data: dict[str, Any] | None = None,
        source_address: str | None = None,
        description: str | None = None,
        sync: bool | None = True,
        request_id: str | None = None,
    ) -> Any:
        """Sign a message"""
        message_sign_create = MessageSignCreate(
            chain_id=chain_id,
            destination_type=destination_type,
            eip712_typed_data=eip712_typed_data,
            source_address=source_address,
            description=description,
            sync=sync,
            request_id=request_id,
        )
        response = await self._transactions_api.message_sign(wallet_uuid, message_sign_create)
        return self._extract_result(response)

    async def payment(
        self: "BaseClient",
        wallet_uuid: str,
        *,
        protocol: Any = None,
        request_id: str | None = None,
        x402_payment_required: str | None = None,
        mpp_www_authenticate: str | None = None,
        mpp_session: Any | None = None,
    ) -> Any:
        """Create payment"""
        payment_create = PaymentCreate(
            protocol=protocol,
            request_id=request_id,
            x402_payment_required=x402_payment_required,
            mpp_www_authenticate=mpp_www_authenticate,
            mpp_session=mpp_session,
        )
        response = await self._transactions_api.payment(wallet_uuid, payment_create)
        return self._extract_result(response)

    async def speedup_transaction(
        self: "BaseClient",
        wallet_uuid: str,
        transaction_uuid: str,
        *,
        request_id: str | None = None,
        fee: Any = None,
        cobo_transaction_id: str | None = None,
    ) -> Any:
        """Speed up transaction"""
        speedup_transaction_request = SpeedupTransactionRequest(
            request_id=request_id, fee=fee, cobo_transaction_id=cobo_transaction_id
        )
        response = await self._transactions_api.speedup_transaction(
            wallet_uuid, transaction_uuid, speedup_transaction_request
        )
        return self._extract_result(response)

    async def transfer_tokens(
        self: "BaseClient",
        wallet_uuid: str,
        *,
        dst_addr: str = None,
        amount: str = None,
        token_id: str | None = "SETH",
        chain_id: str | None = None,
        request_id: str | None = None,
        fee: Any | None = None,
        src_addr: str | None = None,
        sponsor: bool | None = None,
        gas_provider: str | None = None,
        description: str | None = None,
    ) -> Any:
        """Transfer tokens"""
        transfer_create = TransferCreate(
            dst_addr=dst_addr,
            amount=amount,
            token_id=token_id,
            chain_id=chain_id,
            request_id=request_id,
            fee=fee,
            src_addr=src_addr,
            sponsor=sponsor,
            gas_provider=gas_provider,
            description=description,
        )
        response = await self._transactions_api.transfer_tokens(wallet_uuid, transfer_create)
        return self._extract_result(response)

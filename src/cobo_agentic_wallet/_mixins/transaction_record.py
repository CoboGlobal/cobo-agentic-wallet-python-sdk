"""Transactionrecord operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class TransactionRecordMixin:
    """Transactionrecord operations mixin (auto-generated)."""

    _extract_result: Any
    _transaction_records_api: Any

    async def get_user_transaction(
        self: "BaseClient", wallet_uuid: str, record_uuid: str, ext: bool | None = None
    ) -> Any:
        """Get transaction record"""
        response = await self._transaction_records_api.get_user_transaction(
            wallet_uuid, record_uuid, ext
        )
        return self._extract_result(response)

    async def get_user_transaction_by_request_id(
        self: "BaseClient", wallet_uuid: str, request_id: str, ext: bool | None = None
    ) -> Any:
        """Get transaction record by request id"""
        response = await self._transaction_records_api.get_user_transaction_by_request_id(
            wallet_uuid, request_id, ext
        )
        return self._extract_result(response)

    async def get_user_transaction_by_uuid(
        self: "BaseClient", record_uuid: str, ext: bool | None = None
    ) -> Any:
        """Get transaction record by record id"""
        response = await self._transaction_records_api.get_user_transaction_by_uuid(
            record_uuid, ext
        )
        return self._extract_result(response)

    async def list_user_transactions(
        self: "BaseClient",
        wallet_uuid: str | None = None,
        after: str | None = None,
        before: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        status: str | None = None,
        record_type: str | None = None,
        token_id: str | None = None,
        chain_id: str | None = None,
        address_id: str | None = None,
        ext: bool | None = None,
    ) -> Any:
        """List transaction records"""
        response = await self._transaction_records_api.list_user_transactions(
            wallet_uuid,
            after,
            before,
            offset,
            limit,
            status,
            record_type,
            token_id,
            chain_id,
            address_id,
            ext,
        )
        return self._extract_result(response)

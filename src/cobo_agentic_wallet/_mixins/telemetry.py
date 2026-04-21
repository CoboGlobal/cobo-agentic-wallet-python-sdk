"""Telemetry operations mixin (auto-generated).

DO NOT EDIT MANUALLY. Run scripts/generate_mixins.py to regenerate.
"""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from cobo_agentic_wallet._mixins.base import BaseClient


class TelemetryMixin:
    """Telemetry operations mixin (auto-generated)."""

    _extract_result: Any
    _telemetry_api: Any

    async def get_telemetry_config(self: "BaseClient") -> Any:
        """Get telemetry config"""
        response = await self._telemetry_api.get_telemetry_config()
        return self._extract_result(response)

    async def ingest_session_telemetry(self: "BaseClient", session_record: Any) -> Any:
        """Ingest session telemetry"""
        response = await self._telemetry_api.ingest_session_telemetry(session_record)
        return self._extract_result(response)

    async def ingest_telemetry(self: "BaseClient", langfuse_record: Any) -> Any:
        """Ingest CLI telemetry record"""
        response = await self._telemetry_api.ingest_telemetry(langfuse_record)
        return self._extract_result(response)

    async def record_langfuse_raw(self: "BaseClient", langfuse_record: Any) -> Any:
        """Ingest raw Langfuse record"""
        response = await self._telemetry_api.record_langfuse_raw(langfuse_record)
        return self._extract_result(response)

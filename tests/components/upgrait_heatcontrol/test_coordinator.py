"""Coordinator regression tests for the HACS package."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from upgrait_heatcontrol_api import HeatControlApiConnectionError

from custom_components.upgrait_heatcontrol.const import (
    CONF_HA_INSTANCE_ID,
    CONF_HA_PRIVATE_KEY,
    CONF_SERVER_PUBLIC_KEY,
)
from custom_components.upgrait_heatcontrol.coordinator import (
    UpgraitHeatControlCoordinator,
)


@dataclass
class FakeEntry:
    """Minimal config entry stub for coordinator tests."""

    data: dict[str, Any]
    entry_id: str = "entry-id"
    _unload_callbacks: list[Any] = field(default_factory=list)

    def async_on_unload(self, callback: Any) -> None:
        self._unload_callbacks.append(callback)


class FakeConnection:
    """Minimal websocket connection stub."""

    def __init__(self, snapshot: dict[str, Any], *, available: bool = True) -> None:
        self.snapshot = snapshot
        self.available = available
        self.request = AsyncMock()
        self.close = AsyncMock()

    def subscribe(self, _callback: Any) -> Any:
        return lambda: None


@dataclass
class FakeHass:
    """Minimal Home Assistant stub for coordinator unit tests."""

    loop: asyncio.AbstractEventLoop


def _make_entry() -> FakeEntry:
    return FakeEntry(
        data={
            CONF_HA_INSTANCE_ID: "ha-instance-id",
            CONF_HA_PRIVATE_KEY: "ha-private-key",
            CONF_SERVER_PUBLIC_KEY: "server-public-key",
        }
    )


@pytest.mark.asyncio
async def test_coordinator_reconnects_when_existing_connection_is_stale() -> None:
    """Coordinator should recover from a dead websocket object on refresh."""
    stale_connection = FakeConnection({"old": 1}, available=False)
    fresh_connection = FakeConnection({"new": 2})
    client = AsyncMock()
    client.async_connect_and_bind = AsyncMock(return_value=fresh_connection)

    coordinator = UpgraitHeatControlCoordinator(
        FakeHass(asyncio.get_running_loop()), _make_entry(), client
    )
    coordinator.connection = stale_connection

    with patch(
        "custom_components.upgrait_heatcontrol.coordinator.async_refresh_device_metadata",
        AsyncMock(return_value=coordinator.entry),
    ) as refresh_metadata:
        result = await coordinator._async_update_data()

    assert result == {"new": 2}
    assert coordinator.connection is fresh_connection
    stale_connection.close.assert_awaited_once()
    client.async_connect_and_bind.assert_awaited_once()
    refresh_metadata.assert_awaited_once_with(
        coordinator.hass,
        coordinator.entry,
        coordinator.client,
    )


@pytest.mark.asyncio
async def test_cfg_set_retries_once_after_connection_failure() -> None:
    """Write requests should reconnect and retry once after a websocket failure."""
    first_connection = FakeConnection({"topic": 1})
    first_connection.request.side_effect = HeatControlApiConnectionError("reader failed")
    second_connection = FakeConnection({"topic": 2})
    client = AsyncMock()
    client.async_connect_and_bind = AsyncMock(
        side_effect=[first_connection, second_connection]
    )

    coordinator = UpgraitHeatControlCoordinator(
        FakeHass(asyncio.get_running_loop()), _make_entry(), client
    )

    with patch(
        "custom_components.upgrait_heatcontrol.coordinator.async_refresh_device_metadata",
        AsyncMock(side_effect=[coordinator.entry, coordinator.entry]),
    ) as refresh_metadata:
        await coordinator.async_cfg_set("logic.test", True)

    first_connection.request.assert_awaited_once_with(
        "cfg_set", {"key": "logic.test", "value": True}
    )
    first_connection.close.assert_awaited_once()
    second_connection.request.assert_awaited_once_with(
        "cfg_set", {"key": "logic.test", "value": True}
    )
    assert coordinator.connection is second_connection
    assert refresh_metadata.await_count == 2

"""Basic smoke tests for the UPGRAIT HeatControl integration overlay."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock, Mock, patch

from custom_components.upgrait_heatcontrol.const import DEFAULT_PORT, DOMAIN
from custom_components.upgrait_heatcontrol.device_metadata import (
    async_refresh_device_metadata,
)
from upgrait_heatcontrol_api.models import DeviceInfo


def test_basic_constants() -> None:
    assert DOMAIN == "upgrait_heatcontrol"
    assert DEFAULT_PORT == 8001


@dataclass
class FakeEntry:
    """Minimal config entry stub for metadata refresh tests."""

    data: dict


class FakeConfigEntries:
    """Minimal config entries manager stub."""

    def __init__(self) -> None:
        self.async_update_entry = Mock()


class FakeHass:
    """Minimal Home Assistant stub for metadata refresh tests."""

    def __init__(self) -> None:
        self.config_entries = FakeConfigEntries()
        self.device_registry = FakeDeviceRegistry()


class FakeRegistryDevice:
    """Minimal device registry device stub."""

    def __init__(self, sw_version: str | None) -> None:
        self.id = "device-id"
        self.sw_version = sw_version


class FakeDeviceRegistry:
    """Minimal device registry stub."""

    def __init__(self) -> None:
        self.device = FakeRegistryDevice("1613")
        self.async_update_device = Mock()

    def async_get_device(self, identifiers: set[tuple[str, str]]) -> FakeRegistryDevice | None:
        if identifiers == {("upgrait_heatcontrol", "serial-1")}:
            return self.device
        return None


async def test_refresh_entry_device_metadata_updates_stale_firmware_version() -> None:
    """Setup should refresh the cached firmware version from the live UHC ping."""
    hass = FakeHass()
    entry = FakeEntry(
        data={
            "serial": "serial-1",
            "device_version": "1613",
            "server_public_key": "old-key",
        }
    )
    client = AsyncMock()
    client.async_get_device_info.return_value = DeviceInfo(
        serial="serial-1",
        version="1639",
        server_public_key="new-key",
    )

    with patch(
        "custom_components.upgrait_heatcontrol.device_metadata.dr.async_get",
        return_value=hass.device_registry,
    ):
        await async_refresh_device_metadata(hass, entry, client)

    hass.config_entries.async_update_entry.assert_called_once_with(
        entry,
        data={
            "serial": "serial-1",
            "device_version": "1639",
            "server_public_key": "new-key",
        },
    )
    hass.device_registry.async_update_device.assert_called_once_with(
        "device-id",
        sw_version="1639",
    )

"""Shared entity helpers for UPGRAIT HeatControl."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_NAME,
    CONF_DEVICE_VERSION,
    CONF_SERIAL,
    DOMAIN,
    MANUFACTURER,
    MODEL,
)
from .coordinator import UpgraitHeatControlCoordinator


class UpgraitHeatControlEntity(CoordinatorEntity[UpgraitHeatControlCoordinator]):
    """Base entity for UPGRAIT HeatControl."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: UpgraitHeatControlCoordinator) -> None:
        super().__init__(coordinator)
        entry = coordinator.entry
        serial = entry.data[CONF_SERIAL]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=entry.data.get(CONF_DEVICE_NAME),
            sw_version=entry.data.get(CONF_DEVICE_VERSION),
        )

    def _topic_value(self, topic: str) -> Any:
        return self.coordinator.get_topic_value(topic)

"""Binary sensor platform for UPGRAIT HeatControl."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import UpgraitHeatControlCoordinator
from .entity import UpgraitHeatControlEntity
from .entity_descriptions import (
    BOOLEAN_SENSOR_DESCRIPTIONS,
    HeatControlBinarySensorDescription,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up HeatControl binary sensors."""
    coordinator: UpgraitHeatControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        HeatControlBinarySensorEntity(coordinator, description)
        for description in BOOLEAN_SENSOR_DESCRIPTIONS
    )


class HeatControlBinarySensorEntity(UpgraitHeatControlEntity, BinarySensorEntity):
    """HeatControl binary sensor entity."""

    entity_description: HeatControlBinarySensorDescription

    def __init__(
        self,
        coordinator: UpgraitHeatControlCoordinator,
        description: HeatControlBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        serial = coordinator.entry.data["serial"]
        self._attr_unique_id = f"{serial}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        value = self._topic_value(self.entity_description.topic)
        if value is None:
            return None
        return bool(value)

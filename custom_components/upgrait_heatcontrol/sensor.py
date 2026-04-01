"""Sensor platform for UPGRAIT HeatControl."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import UpgraitHeatControlCoordinator
from .entity import UpgraitHeatControlEntity
from .entity_descriptions import SENSOR_DESCRIPTIONS, HeatControlSensorDescription


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up HeatControl sensors."""
    coordinator: UpgraitHeatControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        HeatControlSensorEntity(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class HeatControlSensorEntity(UpgraitHeatControlEntity, SensorEntity):
    """HeatControl sensor entity."""

    entity_description: HeatControlSensorDescription

    def __init__(
        self,
        coordinator: UpgraitHeatControlCoordinator,
        description: HeatControlSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        serial = coordinator.entry.data["serial"]
        self._attr_unique_id = f"{serial}_{description.key}"

    @property
    def native_value(self) -> float | int | str | None:
        value = self._topic_value(self.entity_description.topic)
        if self.entity_description.value_divisor != 1:
            numeric_value: float | None = None
            if isinstance(value, (int, float)):
                numeric_value = float(value)
            elif isinstance(value, str):
                try:
                    numeric_value = float(value)
                except ValueError:
                    numeric_value = None
            if numeric_value is None:
                return None
            return numeric_value / self.entity_description.value_divisor
        if isinstance(value, (int, float, str)):
            return value
        return None

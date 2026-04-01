"""Number platform for UPGRAIT HeatControl."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import UpgraitHeatControlCoordinator
from .entity import UpgraitHeatControlEntity
from .entity_descriptions import HeatControlNumberDescription, NUMBER_DESCRIPTIONS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up HeatControl numbers."""
    coordinator: UpgraitHeatControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        HeatControlNumberEntity(coordinator, description)
        for description in NUMBER_DESCRIPTIONS
    )


class HeatControlNumberEntity(UpgraitHeatControlEntity, NumberEntity):
    """HeatControl number entity."""

    entity_description: HeatControlNumberDescription

    def __init__(
        self,
        coordinator: UpgraitHeatControlCoordinator,
        description: HeatControlNumberDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        serial = coordinator.entry.data["serial"]
        self._attr_unique_id = f"{serial}_{description.key}"

    @property
    def native_value(self) -> float | None:
        value = self._topic_value(self.entity_description.topic)
        if isinstance(value, bool):
            return float(int(value))
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        return None

    async def async_set_native_value(self, value: float) -> None:
        native_value = int(value) if value.is_integer() else float(value)
        await self.coordinator.async_cfg_set(self.entity_description.cfg_key, native_value)

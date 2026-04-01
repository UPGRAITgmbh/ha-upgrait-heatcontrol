"""Switch platform for UPGRAIT HeatControl."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import UpgraitHeatControlCoordinator
from .entity import UpgraitHeatControlEntity
from .entity_descriptions import HeatControlSwitchDescription, SWITCH_DESCRIPTIONS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up HeatControl switches."""
    coordinator: UpgraitHeatControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    descriptions = [
        description
        for description in SWITCH_DESCRIPTIONS
        if not description.requires_topic or coordinator.get_topic_value(description.state_topic) is not None
    ]
    async_add_entities(
        HeatControlSwitchEntity(coordinator, description)
        for description in descriptions
    )


class HeatControlSwitchEntity(UpgraitHeatControlEntity, SwitchEntity):
    """HeatControl switch entity."""

    entity_description: HeatControlSwitchDescription

    def __init__(
        self,
        coordinator: UpgraitHeatControlCoordinator,
        description: HeatControlSwitchDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        serial = coordinator.entry.data["serial"]
        self._attr_unique_id = f"{serial}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        value = self._topic_value(self.entity_description.state_topic)
        if value is None:
            return None
        return bool(value)

    async def async_turn_on(self, **kwargs: object) -> None:
        if self.entity_description.command_type == "actor":
            await self.coordinator.async_actor_set(self.entity_description.actor or "", True)
            return
        await self.coordinator.async_cfg_set(self.entity_description.cfg_key or "", True)

    async def async_turn_off(self, **kwargs: object) -> None:
        if self.entity_description.command_type == "actor":
            await self.coordinator.async_actor_set(self.entity_description.actor or "", False)
            return
        await self.coordinator.async_cfg_set(self.entity_description.cfg_key or "", False)

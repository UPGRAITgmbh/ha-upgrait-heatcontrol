"""Push coordinator for UPGRAIT HeatControl."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from upgrait_heatcontrol_api import HeatControlApiClient, HeatControlConnection

from .const import (
    CONF_HA_INSTANCE_ID,
    CONF_HA_PRIVATE_KEY,
    CONF_SERVER_PUBLIC_KEY,
    DOMAIN,
    LOGGER,
)


class UpgraitHeatControlCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator backed by the connector websocket."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: HeatControlApiClient,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_method=self._async_update_data,
        )
        self.entry = entry
        self.client = client
        self.connection: HeatControlConnection | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        if self.connection is None:
            await self._async_connect()
        return dict(self.connection.snapshot if self.connection is not None else {})

    async def _async_connect(self) -> None:
        self.connection = await self.client.async_connect_and_bind(
            ha_instance_id=self.entry.data[CONF_HA_INSTANCE_ID],
            ha_private_key=self.entry.data[CONF_HA_PRIVATE_KEY],
            server_public_key=self.entry.data[CONF_SERVER_PUBLIC_KEY],
        )
        self.connection.subscribe(self._handle_event)
        self.async_set_updated_data(dict(self.connection.snapshot))

    async def async_cfg_set(self, key: str, value: Any) -> None:
        if self.connection is None:
            await self._async_connect()
        assert self.connection is not None
        await self.connection.request("cfg_set", {"key": key, "value": value})

    async def async_actor_set(self, actor: str, state: bool) -> None:
        if self.connection is None:
            await self._async_connect()
        assert self.connection is not None
        await self.connection.request("actor_set", {"actor": actor, "state": bool(state)})

    async def async_shutdown(self) -> None:
        await super().async_shutdown()
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    async def _handle_event(self, event: dict[str, Any]) -> None:
        current = dict(self.data) if isinstance(self.data, dict) else {}
        topics = event.get("topics")
        if isinstance(topics, dict):
            current = dict(topics)
        elif isinstance(event.get("topic"), str):
            current[event["topic"]] = event.get("value")
        self.async_set_updated_data(current)

    @callback
    def get_topic_value(self, topic: str) -> Any:
        return self.data.get(topic) if isinstance(self.data, dict) else None

"""Helpers for keeping HeatControl device metadata in sync."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from upgrait_heatcontrol_api import HeatControlApiClient

from .const import CONF_DEVICE_VERSION, CONF_SERIAL, CONF_SERVER_PUBLIC_KEY, DOMAIN


async def async_refresh_device_metadata(
    hass: HomeAssistant,
    entry: ConfigEntry,
    client: HeatControlApiClient,
) -> ConfigEntry:
    """Refresh cached device metadata from the live UHC ping endpoint."""
    device = await client.async_get_device_info()
    new_data = dict(entry.data)
    changed = False

    if new_data.get(CONF_DEVICE_VERSION) != device.version:
        new_data[CONF_DEVICE_VERSION] = device.version
        changed = True

    if (
        device.server_public_key
        and new_data.get(CONF_SERVER_PUBLIC_KEY) != device.server_public_key
    ):
        new_data[CONF_SERVER_PUBLIC_KEY] = device.server_public_key
        changed = True

    if changed:
        hass.config_entries.async_update_entry(entry, data=new_data)

    device_registry = dr.async_get(hass)
    registry_device = device_registry.async_get_device(
        identifiers={(DOMAIN, entry.data[CONF_SERIAL])}
    )
    if registry_device is not None and registry_device.sw_version != device.version:
        device_registry.async_update_device(registry_device.id, sw_version=device.version)

    return entry

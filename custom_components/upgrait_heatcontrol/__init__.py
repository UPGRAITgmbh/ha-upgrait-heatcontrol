"""UPGRAIT HeatControl integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import entity_registry as er
from upgrait_heatcontrol_api import (
    HeatControlApiAuthError,
    HeatControlApiClient,
    HeatControlApiConnectionError,
    HeatControlApiError,
)

from .const import DOMAIN
from .coordinator import UpgraitHeatControlCoordinator

DISPLAY_NAME = "UPGRAIT HeatControl"
OLD_ENTITY_ID_PREFIX = "upgrait_gmbh_heatcontrol_"
NEW_ENTITY_ID_PREFIX = "upgrait_heatcontrol_"

PLATFORMS: tuple[Platform, ...] = (
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up UPGRAIT HeatControl from a config entry."""
    entry = await _async_normalize_entry(hass, entry)
    client = HeatControlApiClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        session=async_get_clientsession(hass),
    )
    coordinator = UpgraitHeatControlCoordinator(hass, entry, client)
    try:
        await coordinator.async_config_entry_first_refresh()
    except HeatControlApiAuthError as exc:
        raise ConfigEntryAuthFailed(str(exc)) from exc
    except HeatControlApiConnectionError as exc:
        raise ConfigEntryNotReady(str(exc)) from exc
    except HeatControlApiError as exc:
        raise ConfigEntryNotReady(str(exc)) from exc

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await _async_migrate_entity_ids(hass, entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id, None)
        if coordinator is not None:
            await coordinator.async_shutdown()
    return unload_ok


async def _async_normalize_entry(hass: HomeAssistant, entry: ConfigEntry) -> ConfigEntry:
    new_data = dict(entry.data)
    changed = False

    if new_data.get("device_name") != DISPLAY_NAME:
        new_data["device_name"] = DISPLAY_NAME
        changed = True

    new_title = entry.title
    if "HeatControl" in entry.title and entry.title != f"{DISPLAY_NAME} ({entry.data['serial']})":
        new_title = f"{DISPLAY_NAME} ({entry.data['serial']})"
        changed = True

    if changed:
        hass.config_entries.async_update_entry(entry, data=new_data, title=new_title)
    return entry


async def _async_migrate_entity_ids(hass: HomeAssistant, entry: ConfigEntry) -> None:
    registry = er.async_get(hass)
    for registry_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        entity_id = registry_entry.entity_id
        if OLD_ENTITY_ID_PREFIX not in entity_id:
            continue
        new_entity_id = entity_id.replace(OLD_ENTITY_ID_PREFIX, NEW_ENTITY_ID_PREFIX, 1)
        try:
            registry.async_update_entity(entity_id, new_entity_id=new_entity_id)
        except ValueError:
            continue

"""Config flow for UPGRAIT HeatControl."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import data_entry_flow
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.instance_id import async_get as async_get_instance_id
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from upgrait_heatcontrol_api import (
    HeatControlApiAuthError,
    HeatControlApiClient,
    HeatControlApiConnectionError,
    HeatControlApiError,
    HeatControlApiInvalidPinError,
    generate_keypair,
)
from upgrait_heatcontrol_api.models import DeviceInfo, PairingStartResult

from .const import (
    CONF_DEVICE_NAME,
    CONF_DEVICE_VERSION,
    CONF_HA_INSTANCE_ID,
    CONF_HA_PRIVATE_KEY,
    CONF_HA_PUBLIC_KEY,
    CONF_SERIAL,
    CONF_SERVER_PUBLIC_KEY,
    DEFAULT_PORT,
    DOMAIN,
    INTEGRATION_VERSION,
    LOGGER,
    MANUFACTURER,
    MODEL,
)

CONF_PIN = "pin"
DISPLAY_NAME = "UPGRAIT HeatControl"


async def async_validate_host(
    hass: HomeAssistant, data: dict[str, Any]
) -> tuple[DeviceInfo, HeatControlApiClient]:
    """Validate the host entered by the user or discovered by Zeroconf."""
    client = HeatControlApiClient(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        session=async_get_clientsession(hass),
    )
    device = await client.async_get_device_info()
    return device, client


class UpgraitHeatControlConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for UPGRAIT HeatControl."""

    VERSION = 1

    _client: HeatControlApiClient | None = None
    _device: DeviceInfo | None = None
    _host: str | None = None
    _port: int = DEFAULT_PORT
    _ha_instance_id: str | None = None
    _display_name: str | None = None
    _ha_private_key: str | None = None
    _ha_public_key: str | None = None
    _server_public_key: str | None = None
    _pairing_start: PairingStartResult | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial manual step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await self._async_prepare_pairing(
                    host=str(user_input[CONF_HOST]),
                    port=int(user_input[CONF_PORT]),
                )
            except HeatControlApiConnectionError as exc:
                LOGGER.debug("Failed to connect to HeatControl during setup: %s", exc)
                errors["base"] = "cannot_connect"
            except HeatControlApiError:
                LOGGER.exception("Unexpected HeatControl API error during setup")
                errors["base"] = "unknown"
            except Exception:
                LOGGER.exception("Unexpected error during HeatControl setup")
                errors["base"] = "unknown"
            else:
                return await self.async_step_pair_confirm()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                }
            ),
            errors=errors,
        )

    async def async_step_pair_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm pairing by entering the PIN shown on the UHC."""
        assert self._client is not None
        assert self._device is not None
        assert self._host is not None
        assert self._ha_instance_id is not None
        assert self._display_name is not None
        assert self._ha_private_key is not None
        assert self._ha_public_key is not None
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                confirm_result = await self._client.async_confirm_pairing(
                    pin=str(user_input[CONF_PIN]).strip(),
                    ha_instance_id=self._ha_instance_id,
                    display_name=self._display_name,
                    integration_version=INTEGRATION_VERSION,
                    ha_public_key=self._ha_public_key,
                )
            except HeatControlApiInvalidPinError:
                errors["base"] = "invalid_pin"
            except HeatControlApiAuthError:
                errors["base"] = "pairing_not_active"
            except HeatControlApiConnectionError as exc:
                LOGGER.debug("Failed to confirm HeatControl pairing: %s", exc)
                errors["base"] = "cannot_connect"
            except HeatControlApiError:
                LOGGER.exception("Unexpected HeatControl API error during pairing confirm")
                errors["base"] = "unknown"
            except Exception:
                LOGGER.exception("Unexpected error during HeatControl pairing confirm")
                errors["base"] = "unknown"
            else:
                entry_data = {
                    CONF_HOST: self._host,
                    CONF_PORT: self._port,
                    CONF_SERIAL: self._device.serial,
                    CONF_DEVICE_NAME: DISPLAY_NAME,
                    CONF_DEVICE_VERSION: self._device.version,
                    CONF_HA_INSTANCE_ID: self._ha_instance_id,
                    CONF_HA_PRIVATE_KEY: self._ha_private_key,
                    CONF_HA_PUBLIC_KEY: self._ha_public_key,
                    CONF_SERVER_PUBLIC_KEY: confirm_result.server_public_key
                    or self._server_public_key
                    or self._device.server_public_key,
                }
                title = f"{DISPLAY_NAME} ({self._device.serial})"
                return self.async_create_entry(title=title, data=entry_data)

        description_placeholders = {
            "host": self._host,
            "port": str(self._port),
            "display_name": self._display_name,
            "expires_at": str(self._pairing_start.expires_at if self._pairing_start else ""),
            "existing_binding": (
                self._pairing_start.existing_binding_display_name
                if self._pairing_start and self._pairing_start.existing_binding_display_name
                else "-"
            ),
        }
        return self.async_show_form(
            step_id="pair_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PIN): str}),
            description_placeholders=description_placeholders,
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle Zeroconf discovery."""
        host = discovery_info.host
        port = discovery_info.port or DEFAULT_PORT
        try:
            device, client = await async_validate_host(
                self.hass, {CONF_HOST: host, CONF_PORT: port}
            )
            await self.async_set_unique_id(device.serial)
            self._abort_if_unique_id_configured(
                updates={CONF_HOST: host, CONF_PORT: port}
            )
        except HeatControlApiConnectionError as exc:
            LOGGER.debug(
                "Failed to connect to HeatControl during zeroconf setup: %s", exc
            )
            return self.async_abort(reason="cannot_connect")
        except HeatControlApiError:
            LOGGER.exception("Unexpected HeatControl API error during zeroconf setup")
            return self.async_abort(reason="cannot_connect")
        except data_entry_flow.AbortFlow:
            raise
        except Exception:
            LOGGER.exception("Unexpected error during HeatControl zeroconf setup")
            return self.async_abort(reason="cannot_connect")

        self._client = client
        self._device = device
        self._host = host
        self._port = port
        self._server_public_key = device.server_public_key
        self.context["title_placeholders"] = {"name": DISPLAY_NAME}
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Wait for user confirmation before starting pairing on the UHC."""
        assert self._client is not None
        assert self._device is not None
        assert self._host is not None

        if user_input is not None:
            try:
                await self._async_prepare_pairing(host=self._host, port=self._port)
            except HeatControlApiConnectionError as exc:
                LOGGER.debug(
                    "Failed to connect to HeatControl during zeroconf confirm: %s", exc
                )
                return self.async_abort(reason="cannot_connect")
            except HeatControlApiError:
                LOGGER.exception(
                    "Unexpected HeatControl API error during zeroconf confirm"
                )
                return self.async_abort(reason="cannot_connect")
            except data_entry_flow.AbortFlow:
                raise
            except Exception:
                LOGGER.exception("Unexpected error during HeatControl zeroconf confirm")
                return self.async_abort(reason="cannot_connect")
            return await self.async_step_pair_confirm()

        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={
                "host": self._host,
                "port": str(self._port),
                "name": DISPLAY_NAME,
            },
        )

    async def _async_prepare_pairing(self, *, host: str, port: int) -> None:
        device, client = await async_validate_host(
            self.hass, {CONF_HOST: host, CONF_PORT: port}
        )
        await self.async_set_unique_id(device.serial)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host, CONF_PORT: port})

        self._client = client
        self._device = device
        self._host = host
        self._port = port
        self._ha_instance_id = await async_get_instance_id(self.hass)
        self._display_name = self.hass.config.location_name or "Home Assistant"
        self._ha_private_key, self._ha_public_key = generate_keypair()
        self._server_public_key = device.server_public_key
        self._pairing_start = await client.async_start_pairing(
            ha_instance_id=self._ha_instance_id,
            display_name=self._display_name,
            integration_version=INTEGRATION_VERSION,
        )
        if self._pairing_start.server_public_key:
            self._server_public_key = self._pairing_start.server_public_key

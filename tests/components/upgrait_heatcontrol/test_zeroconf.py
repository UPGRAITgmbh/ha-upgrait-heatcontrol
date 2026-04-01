"""Zeroconf config flow tests for UPGRAIT HeatControl."""

from __future__ import annotations

from ipaddress import ip_address
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import SOURCE_ZEROCONF
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from upgrait_heatcontrol_api.models import DeviceInfo, PairingConfirmResult, PairingStartResult

from custom_components.upgrait_heatcontrol.const import (
    CONF_DEVICE_NAME,
    CONF_HA_INSTANCE_ID,
    CONF_HA_PRIVATE_KEY,
    CONF_HA_PUBLIC_KEY,
    CONF_SERIAL,
    CONF_SERVER_PUBLIC_KEY,
    DEFAULT_PORT,
    DOMAIN,
)


MOCK_ZEROCONF = ZeroconfServiceInfo(
    ip_address=ip_address("192.0.2.1"),
    ip_addresses=[ip_address("192.0.2.1")],
    port=8001,
    hostname="uhc-1000000068971dd6.local.",
    type="_upgrait-hc._tcp.local.",
    name="UPGRAIT HeatControl 1000000068971dd6._upgrait-hc._tcp.local.",
    properties={
        "vendor": "UPGRAIT GmbH",
        "model": "HeatControl",
        "version": "1609",
    },
)


async def test_zeroconf_pairing_flow(hass) -> None:
    """Test zeroconf discovery asks for confirmation before pairing."""
    mock_client = AsyncMock()
    mock_client.async_start_pairing.return_value = PairingStartResult(
        expires_at=1_777_000_000_000,
        pairing_active=True,
        replaces_existing_binding=False,
        existing_binding_display_name=None,
        server_public_key="server-public-key",
    )
    mock_client.async_confirm_pairing.return_value = PairingConfirmResult(
        ha_instance_id="ha-instance-id",
        display_name="Home Assistant",
        integration_version="0.1.0",
        revision=1,
        confirmed_at=1_777_000_000_100,
        server_public_key="server-public-key",
    )

    with (
        patch(
            "custom_components.upgrait_heatcontrol.async_setup_entry",
            return_value=True,
        ),
        patch(
            "custom_components.upgrait_heatcontrol.config_flow.async_validate_host",
            return_value=(
                DeviceInfo(
                    serial="1000000068971dd6d83add722633d83add722634",
                    version="1609",
                    server_public_key="server-public-key",
                    manufacturer="UPGRAIT GmbH",
                    model="HeatControl",
                    name="UPGRAIT HeatControl",
                ),
                mock_client,
            ),
        ),
        patch(
            "custom_components.upgrait_heatcontrol.config_flow.async_get_instance_id",
            return_value="ha-instance-id",
        ),
        patch(
            "custom_components.upgrait_heatcontrol.config_flow.generate_keypair",
            return_value=("ha-private-key", "ha-public-key"),
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_ZEROCONF},
            data=MOCK_ZEROCONF,
        )

        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "zeroconf_confirm"
        assert result["description_placeholders"]["host"] == "192.0.2.1"
        assert result["description_placeholders"]["port"] == "8001"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {},
        )

        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "pair_confirm"
        assert result["description_placeholders"]["host"] == "192.0.2.1"
        assert result["description_placeholders"]["port"] == "8001"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"pin": "123456"},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "UPGRAIT HeatControl (1000000068971dd6d83add722633d83add722634)"
    assert result["data"][CONF_HOST] == "192.0.2.1"
    assert result["data"][CONF_PORT] == DEFAULT_PORT
    assert result["data"][CONF_SERIAL] == "1000000068971dd6d83add722633d83add722634"
    assert result["data"][CONF_DEVICE_NAME] == "UPGRAIT HeatControl"
    assert result["data"][CONF_HA_INSTANCE_ID] == "ha-instance-id"
    assert result["data"][CONF_HA_PRIVATE_KEY] == "ha-private-key"
    assert result["data"][CONF_HA_PUBLIC_KEY] == "ha-public-key"
    assert result["data"][CONF_SERVER_PUBLIC_KEY] == "server-public-key"

    mock_client.async_start_pairing.assert_awaited_once()
    mock_client.async_confirm_pairing.assert_awaited_once()

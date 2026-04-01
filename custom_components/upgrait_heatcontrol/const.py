"""Constants for the UPGRAIT HeatControl integration."""

from __future__ import annotations

import logging

from upgrait_heatcontrol_api.discovery import (
    DEFAULT_PORT,
    MANUFACTURER,
    MODEL,
    SERVICE_TYPE,
)

DOMAIN = "upgrait_heatcontrol"
LOGGER = logging.getLogger(__package__)
INTEGRATION_VERSION = "0.1.1"

CONF_HA_INSTANCE_ID = "ha_instance_id"
CONF_HA_PRIVATE_KEY = "ha_private_key"
CONF_HA_PUBLIC_KEY = "ha_public_key"
CONF_SERVER_PUBLIC_KEY = "server_public_key"
CONF_SERIAL = "serial"
CONF_DEVICE_NAME = "device_name"
CONF_DEVICE_VERSION = "device_version"

TOPIC_PREFIX = "UCH/"

__all__ = [
    "CONF_DEVICE_NAME",
    "CONF_DEVICE_VERSION",
    "CONF_HA_INSTANCE_ID",
    "CONF_HA_PRIVATE_KEY",
    "CONF_HA_PUBLIC_KEY",
    "CONF_SERIAL",
    "CONF_SERVER_PUBLIC_KEY",
    "DEFAULT_PORT",
    "DOMAIN",
    "INTEGRATION_VERSION",
    "LOGGER",
    "MANUFACTURER",
    "MODEL",
    "SERVICE_TYPE",
    "TOPIC_PREFIX",
]

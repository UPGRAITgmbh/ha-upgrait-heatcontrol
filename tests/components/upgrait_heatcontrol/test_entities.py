"""Entity behavior tests for the HACS package."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock

import pytest

from custom_components.upgrait_heatcontrol.entity_descriptions import (
    NUMBER_DESCRIPTIONS,
    SENSOR_DESCRIPTIONS,
    SWITCH_DESCRIPTIONS,
)
from custom_components.upgrait_heatcontrol.number import HeatControlNumberEntity
from custom_components.upgrait_heatcontrol.sensor import HeatControlSensorEntity
from custom_components.upgrait_heatcontrol.switch import HeatControlSwitchEntity


@dataclass
class FakeEntry:
    """Minimal config entry stub for entity tests."""

    data: dict[str, Any]


class FakeCoordinator:
    """Minimal coordinator stub for entity tests."""

    def __init__(self, topics: dict[str, Any]) -> None:
        self.entry = FakeEntry(
            data={
                "serial": "serial-1",
                "device_name": "UPGRAIT HeatControl",
                "device_version": "1609",
            }
        )
        self.data = topics
        self.last_update_success = True
        self.async_cfg_set = AsyncMock()
        self.async_actor_set = AsyncMock()

    def async_add_listener(self, _callback: Any, _context: Any = None) -> Any:
        return lambda: None

    def get_topic_value(self, topic: str) -> Any:
        return self.data.get(topic)


def test_sensor_value_divisor_and_invalid_string() -> None:
    """Energy sensors should scale numeric strings and reject invalid text."""
    description = next(
        item for item in SENSOR_DESCRIPTIONS if item.key == "energy_total_import"
    )

    scaled = HeatControlSensorEntity(
        FakeCoordinator({description.topic: "25218680"}), description
    )
    invalid = HeatControlSensorEntity(
        FakeCoordinator({description.topic: "not-a-number"}), description
    )

    assert scaled.native_value == 25218.68
    assert invalid.native_value is None


@pytest.mark.asyncio
async def test_number_entity_coerces_and_writes_native_value() -> None:
    """Number entities should coerce values and forward integer writes as ints."""
    description = NUMBER_DESCRIPTIONS[0]
    coordinator = FakeCoordinator({description.topic: "42"})
    entity = HeatControlNumberEntity(coordinator, description)

    assert entity.native_value == 42.0

    await entity.async_set_native_value(55.0)

    coordinator.async_cfg_set.assert_awaited_once_with(description.cfg_key, 55)


@pytest.mark.asyncio
async def test_switch_entities_delegate_cfg_and_actor_commands() -> None:
    """Switch entities should delegate cfg and actor writes to the coordinator."""
    cfg_description = next(
        item for item in SWITCH_DESCRIPTIONS if item.key == "holiday_enabled"
    )
    actor_description = next(
        item for item in SWITCH_DESCRIPTIONS if item.key == "circulation_pump"
    )
    coordinator = FakeCoordinator(
        {
            cfg_description.state_topic: False,
            actor_description.state_topic: True,
        }
    )

    cfg_entity = HeatControlSwitchEntity(coordinator, cfg_description)
    actor_entity = HeatControlSwitchEntity(coordinator, actor_description)

    await cfg_entity.async_turn_on()
    await actor_entity.async_turn_off()

    coordinator.async_cfg_set.assert_awaited_once_with(cfg_description.cfg_key or "", True)
    coordinator.async_actor_set.assert_awaited_once_with(
        actor_description.actor or "", False
    )

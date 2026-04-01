"""Entity descriptions for UPGRAIT HeatControl."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.number import NumberDeviceClass, NumberEntityDescription, NumberMode
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)


@dataclass(frozen=True, kw_only=True)
class HeatControlSensorDescription(SensorEntityDescription):
    topic: str
    value_divisor: float = 1.0


@dataclass(frozen=True, kw_only=True)
class HeatControlBinarySensorDescription(BinarySensorEntityDescription):
    topic: str


@dataclass(frozen=True, kw_only=True)
class HeatControlSwitchDescription(SwitchEntityDescription):
    state_topic: str
    command_type: str = "cfg"
    cfg_key: str | None = None
    actor: str | None = None
    requires_topic: bool = False
    support_topic: str | None = None
    topic: str | None = None


@dataclass(frozen=True, kw_only=True)
class HeatControlNumberDescription(NumberEntityDescription):
    cfg_key: str
    topic: str


SENSOR_DESCRIPTIONS: tuple[HeatControlSensorDescription, ...] = (
    HeatControlSensorDescription(
        key="grid_watts",
        translation_key="grid_watts",
        name="Grid Power",
        topic="UCH/energy/gridWatts",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HeatControlSensorDescription(
        key="grid_voltage",
        translation_key="grid_voltage",
        name="Grid Voltage",
        topic="UCH/energy/gridVoltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HeatControlSensorDescription(
        key="grid_current",
        translation_key="grid_current",
        name="Grid Current",
        topic="UCH/energy/gridCurrent",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HeatControlSensorDescription(
        key="powermeter_frequency",
        translation_key="powermeter_frequency",
        name="Power Meter Frequency",
        topic="UCH/powermeter/frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HeatControlSensorDescription(
        key="powermeter_total_current",
        translation_key="powermeter_total_current",
        name="Power Meter Total Current",
        topic="UCH/powermeter/total_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HeatControlSensorDescription(
        key="powermeter_total_import",
        translation_key="powermeter_total_import",
        name="Power Meter Total Import",
        topic="UCH/powermeter/total_import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_divisor=1000,
    ),
    HeatControlSensorDescription(
        key="energy_total_import",
        translation_key="energy_total_import",
        name="Grid Total Import",
        topic="UCH/energy/total_import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_divisor=1000,
    ),
    HeatControlSensorDescription(
        key="energy_total_export",
        translation_key="energy_total_export",
        name="Grid Total Export",
        topic="UCH/energy/total_export",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_divisor=1000,
    ),
    HeatControlSensorDescription(
        key="reservoir_top_temperature",
        translation_key="reservoir_top_temperature",
        name="Reservoir Top Temperature",
        topic="UCH/hal/reservoir/1/t_top",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HeatControlSensorDescription(
        key="reservoir_bottom_temperature",
        translation_key="reservoir_bottom_temperature",
        name="Reservoir Bottom Temperature",
        topic="UCH/hal/reservoir/1/t_bottom",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HeatControlSensorDescription(
        key="circuit_1_forerun_temperature",
        translation_key="circuit_1_forerun_temperature",
        name="Circuit 1 Forerun Temperature",
        topic="UCH/hal/circuits/1/t_forerun",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HeatControlSensorDescription(
        key="circuit_1_backrun_temperature",
        translation_key="circuit_1_backrun_temperature",
        name="Circuit 1 Backrun Temperature",
        topic="UCH/hal/circuits/1/t_backrun",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

binary = BinarySensorDeviceClass
BOOLEAN_SENSOR_DESCRIPTIONS: tuple[HeatControlBinarySensorDescription, ...] = (
    HeatControlBinarySensorDescription(
        key="has_pv",
        translation_key="has_pv",
        name="PV Available",
        topic="UCH/energy/hasPv",
        device_class=binary.POWER,
    ),
    HeatControlBinarySensorDescription(
        key="has_battery",
        translation_key="has_battery",
        name="Battery Available",
        topic="UCH/energy/hasBattery",
        device_class=binary.BATTERY_CHARGING,
    ),
    HeatControlBinarySensorDescription(
        key="heater_active",
        translation_key="heater_active",
        name="Heater Active",
        topic="UCH/hal/heaters/1/active",
        device_class=binary.HEAT,
    ),
)

SWITCH_DESCRIPTIONS: tuple[HeatControlSwitchDescription, ...] = (
    HeatControlSwitchDescription(
        key="circuit_1_enabled",
        translation_key="circuit_1_enabled",
        name="Circuit 1",
        cfg_key="logic.circuits.1.enabled",
        state_topic="UCH/cfg/logic/circuits/1/enabled",
    ),
    HeatControlSwitchDescription(
        key="circuit_2_enabled",
        translation_key="circuit_2_enabled",
        name="Circuit 2",
        cfg_key="logic.circuits.2.enabled",
        state_topic="UCH/cfg/logic/circuits/2/enabled",
    ),
    HeatControlSwitchDescription(
        key="holiday_enabled",
        translation_key="holiday_enabled",
        name="Holiday Mode",
        cfg_key="scheduler.holiday.enabled",
        state_topic="UCH/cfg/scheduler/holiday/enabled",
    ),
    HeatControlSwitchDescription(
        key="maintenance_enabled",
        translation_key="maintenance_enabled",
        name="Maintenance",
        cfg_key="scheduler.maintenance.enabled",
        state_topic="UCH/cfg/scheduler/maintenance/enabled",
    ),
    HeatControlSwitchDescription(
        key="heater_1_flickerfree",
        translation_key="heater_1_flickerfree",
        name="Heater 1 Flickerfree Mode",
        cfg_key="logic.heaters.1.flickerfree",
        state_topic="UCH/cfg/logic/heaters/1/flickerfree",
    ),
    HeatControlSwitchDescription(
        key="circulation_pump",
        translation_key="circulation_pump",
        name="Circulation Pump",
        state_topic="UCH/actors/circulator",
        command_type="actor",
        actor="circulator",
        requires_topic=True,
    ),
)

NUMBER_DESCRIPTIONS: tuple[HeatControlNumberDescription, ...] = (
    HeatControlNumberDescription(
        key="reservoir_1_minimal_temperature",
        translation_key="reservoir_1_minimal_temperature",
        name="Reservoir 1 Minimal Temperature",
        cfg_key="logic.reservoirs.1.mintemperature",
        topic="UCH/cfg/logic/reservoirs/1/mintemperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.BOX,
    ),
)

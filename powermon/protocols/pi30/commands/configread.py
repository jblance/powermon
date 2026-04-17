""" pi30 commands that read configuration values """

from powermon.protocols.constants import (
    BATTERY_TYPES,
    OUTPUT_MODES,
    OUTPUT_SOURCE_PRIORITIES,
)

from powermon.protocols.model import (
    CommandCategory,
    CommandDefinition,
    ParameterSpec,
    ReadingDefinition,
    RequestSpec,
    ResponseSpec,
)
from powermon.protocols.parsers import parse_pi30_ascii, parse_pi30_flags

QPIRI = CommandDefinition(
    command_id="QPIRI",
    name="Inverter Settings",
    description="Get the current configuration settings of the inverter",
    category=CommandCategory.CONFIG_READ,

    request=RequestSpec(command="QPIRI"),

    response=ResponseSpec(
        parser=parse_pi30_ascii,
        min_fields=24,   # observed minimum
    ),

    readings={
        "ac_input_voltage": ReadingDefinition(index=0, label="AC Input Voltage", unit="V", dtype=float),
        "ac_input_current": ReadingDefinition(index=1, label="AC Input Current", unit="A", dtype=float),
        "ac_output_voltage": ReadingDefinition(index=2, label="AC Output Voltage", unit="V", dtype=float),
        "ac_output_frequency": ReadingDefinition(index=3, label="AC Output Frequency", unit="Hz", dtype=float),
        "ac_output_current": ReadingDefinition(index=4, label="AC Output Current", unit="A", dtype=float),
        "ac_output_apparent_power": ReadingDefinition(index=5, label="AC Output Apparent Power", unit="VA", dtype=int),
        "ac_output_active_power": ReadingDefinition(index=6, label="AC Output Active Power", unit="W", dtype=int),
        "battery_voltage": ReadingDefinition(index=7, label="Battery Voltage", unit="V", dtype=float),
        "battery_recharge_voltage": ReadingDefinition(index=8, label="Battery Recharge Voltage", unit="V", dtype=float),
        "battery_under_voltage": ReadingDefinition(index=9, label="Battery Under Voltage", unit="V", dtype=float),
        "battery_bulk_charge_voltage": ReadingDefinition(index=10, label="Battery Bulk Charge Voltage", unit="V", dtype=float),
        "battery_float_charge_voltage": ReadingDefinition(index=11, label="Battery Float Charge Voltage", unit="V", dtype=float),
        "battery_type": ReadingDefinition(
            index=12,
            label="Battery Type",
            unit="",
            dtype=str,
            description=f"Options: {BATTERY_TYPES}",
        ),
        "max_ac_charging_current": ReadingDefinition(index=13, label="Max AC Charging Current", unit="A", dtype=int),
        "max_charging_current": ReadingDefinition(index=14, label="Max Charging Current", unit="A", dtype=int),
        "input_voltage_range": ReadingDefinition(
            index=15,
            label="Input Voltage Range",
            unit="",
            dtype=str,
            description="Options: Appliance / UPS",
        ),
        "output_source_priority": ReadingDefinition(
            index=16,
            label="Output Source Priority",
            unit="",
            dtype=str,
            description=f"Options: {OUTPUT_SOURCE_PRIORITIES}",
        ),
        "charger_source_priority": ReadingDefinition(
            index=17,
            label="Charger Source Priority",
            unit="",
            dtype=str,
            description="Utility first / Solar first / Solar + Utility / Solar only",
        ),
        "max_parallel_units": ReadingDefinition(
            index=18,
            label="Max Parallel Units",
            unit="",
            dtype=str,
            description="May be '-' or unset on some models",
        ),
        "machine_type": ReadingDefinition(
            index=19,
            label="Machine Type",
            unit="",
            dtype=str,
            description="00=Grid tie, 01=Off-grid, 10=Hybrid",
        ),
        "topology": ReadingDefinition(
            index=20,
            label="Topology",
            unit="",
            dtype=str,
            description="transformerless / transformer",
        ),
        "output_mode": ReadingDefinition(
            index=21,
            label="Output Mode",
            unit="",
            dtype=str,
            description=f"Options: {OUTPUT_MODES}",
        ),
        "battery_redischarge_voltage": ReadingDefinition(
            index=22,
            label="Battery Redischarge Voltage",
            unit="V",
            dtype=float,
        ),
        "pv_ok_condition": ReadingDefinition(
            index=23,
            label="PV OK Condition",
            unit="",
            dtype=str,
        ),
        "pv_power_balance": ReadingDefinition(
            index=24,
            label="PV Power Balance",
            unit="",
            dtype=str,
        ),
        "max_cv_charge_time": ReadingDefinition(
            index=25,
            label="Max CV Charge Time",
            unit="min",
            dtype=int,
            optional=True,  # not present on all models / firmware versions
        ),
        "operation_logic": ReadingDefinition(
            index=26,
            label="Operation Logic",
            unit="",
            dtype=str,
            description="Automatic / On-line / ECO",
            optional=True,  # not present on all models / firmware versions
        ),
    },
)

READ_COMMANDS: dict[str, CommandDefinition] = {
    "QPIRI": QPIRI,
}
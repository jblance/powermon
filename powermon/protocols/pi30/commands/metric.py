""" pi30 commands that read metric values (ie real-time and fast changes measurements) """

from powermon.protocols.model import (
    CommandCategory,
    CommandDefinition,
    ParameterSpec,
    ReadingDefinition,
    RequestSpec,
    ResponseSpec,
)
from powermon.protocols.parsers import parse_pi30_ascii, parse_pi30_flags

QPIGS = CommandDefinition(
    command_id="QPIGS",
    name="General Status",
    description="Read real-time inverter general status measurements",
    category=CommandCategory.METRIC,

    request=RequestSpec(
        command="QPIGS",
    ),

    response=ResponseSpec(
        parser=parse_pi30_ascii,
        min_fields=20,
        max_fields=21,  # some variants append extra fields
    ),

    readings={
        "ac_input_voltage": ReadingDefinition(
            index=0,
            label="AC Input Voltage",
            unit="V",
            dtype=float,
        ),
        "ac_input_frequency": ReadingDefinition(
            index=1,
            label="AC Input Frequency",
            unit="Hz",
            dtype=float,
        ),
        "ac_output_voltage": ReadingDefinition(
            index=2,
            label="AC Output Voltage",
            unit="V",
            dtype=float,
        ),
        "ac_output_frequency": ReadingDefinition(
            index=3,
            label="AC Output Frequency",
            unit="Hz",
            dtype=float,
        ),
        "ac_output_apparent_power": ReadingDefinition(
            index=4,
            label="AC Output Apparent Power",
            unit="VA",
            dtype=int,
        ),
        "ac_output_active_power": ReadingDefinition(
            index=5,
            label="AC Output Active Power",
            unit="W",
            dtype=int,
        ),
        "output_load_percent": ReadingDefinition(
            index=6,
            label="Output Load Percentage",
            unit="%",
            dtype=int,
        ),
        "bus_voltage": ReadingDefinition(
            index=7,
            label="Bus Voltage",
            unit="V",
            dtype=int,
        ),
        "battery_voltage": ReadingDefinition(
            index=8,
            label="Battery Voltage",
            unit="V",
            dtype=float,
        ),
        "battery_charging_current": ReadingDefinition(
            index=9,
            label="Battery Charging Current",
            unit="A",
            dtype=int,
        ),
        "battery_capacity": ReadingDefinition(
            index=10,
            label="Battery Capacity",
            unit="%",
            dtype=int,
        ),
        "inverter_temperature": ReadingDefinition(
            index=11,
            label="Inverter Temperature",
            unit="°C",
            dtype=int,
        ),
        "pv_input_current": ReadingDefinition(
            index=12,
            label="PV Input Current",
            unit="A",
            dtype=float,
        ),
        "pv_input_voltage": ReadingDefinition(
            index=13,
            label="PV Input Voltage",
            unit="V",
            dtype=float,
        ),
        "battery_voltage_scc": ReadingDefinition(
            index=14,
            label="Battery Voltage (SCC)",
            unit="V",
            dtype=float,
        ),
        "battery_discharge_current": ReadingDefinition(
            index=15,
            label="Battery Discharge Current",
            unit="A",
            dtype=int,
        ),

        # Device status flags packed as ASCII bits
        "device_status_bits": ReadingDefinition(
            index=16,
            label="Device Status Bits",
            unit="",
            dtype=str,
            description="Binary status flags bitfield",
        ),

        # Reserved / unused fields
        "reserved_1": ReadingDefinition(index=17,  label="Reserved 1", unit="", dtype=int),
        "reserved_2": ReadingDefinition(index=18, label="Reserved 2", unit="", dtype=int),

        "pv_input_power": ReadingDefinition(
            index=19,
            label="PV Input Power",
            unit="W",
            dtype=int,
        ),

        "device_status2_bits": ReadingDefinition(
            index=20,
            label="Device Status Bits 2",
            unit="",
            dtype=str,
            description="Secondary binary status bitfield",
        ),
    },

)

METRIC_COMMANDS: dict[str, CommandDefinition] = {
    "QPIGS": QPIGS,
}
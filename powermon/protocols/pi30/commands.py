import re

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

QID = CommandDefinition(
    id="QID",
    title="Serial Number",
    description="Get the Serial Number of the Inverter",
    category=CommandCategory.IDENTITY,

    request=RequestSpec(command="QID"),
    response=ResponseSpec(
        parser=parse_pi30_ascii,
        min_fields=1,
        max_fields=1,
    ),

    readings={
        "serial_number": ReadingDefinition(
            index=0,
            label="Serial Number",
            unit="",
            dtype=str,
        ),
    },

)

QPIGS = CommandDefinition(
    id="QPIGS",
    title="General Status",
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
        "reserved_1": ReadingDefinition(17, "Reserved 1", "", int),
        "reserved_2": ReadingDefinition(18, "Reserved 2", "", int),

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

QPIWS = CommandDefinition(
    id="QPIWS",
    title="Warning Status",
    description="Get any active Warning Status flags",
    category=CommandCategory.STATUS,

    request=RequestSpec(command="QPIWS"),
    response=ResponseSpec(
        parser=parse_pi30_flags,
        min_fields=35,
    ),

    readings={
        "pv_loss_warning": ReadingDefinition(0, "PV loss warning", "", bool),
        "battery_low_alarm": ReadingDefinition(12, "Battery low alarm warning", "", bool),
        "battery_equalisation": ReadingDefinition(35, "Battery equalisation warning", "", bool),
    },

)

QPIRI = CommandDefinition(
    id="QPIRI",
    title="Inverter Settings",
    description="Get the current configuration settings of the inverter",
    category=CommandCategory.CONFIG_READ,

    request=RequestSpec(command="QPIRI"),

    response=ResponseSpec(
        parser=parse_pi30_ascii,
        min_fields=24,   # observed minimum
    ),

    readings={
        "ac_input_voltage": ReadingDefinition(0, "AC Input Voltage", "V", float),
        "ac_input_current": ReadingDefinition(1, "AC Input Current", "A", float),

        "ac_output_voltage": ReadingDefinition(2, "AC Output Voltage", "V", float),
        "ac_output_frequency": ReadingDefinition(3, "AC Output Frequency", "Hz", float),
        "ac_output_current": ReadingDefinition(4, "AC Output Current", "A", float),

        "ac_output_apparent_power": ReadingDefinition(5, "AC Output Apparent Power", "VA", int),
        "ac_output_active_power": ReadingDefinition(6, "AC Output Active Power", "W", int),

        "battery_voltage": ReadingDefinition(7, "Battery Voltage", "V", float),
        "battery_recharge_voltage": ReadingDefinition(8, "Battery Recharge Voltage", "V", float),
        "battery_under_voltage": ReadingDefinition(9, "Battery Under Voltage", "V", float),
        "battery_bulk_charge_voltage": ReadingDefinition(10, "Battery Bulk Charge Voltage", "V", float),
        "battery_float_charge_voltage": ReadingDefinition(11, "Battery Float Charge Voltage", "V", float),

        "battery_type": ReadingDefinition(
            12,
            "Battery Type",
            "",
            str,
            description=f"Options: {BATTERY_TYPES}",
        ),

        "max_ac_charging_current": ReadingDefinition(13, "Max AC Charging Current", "A", int),
        "max_charging_current": ReadingDefinition(14, "Max Charging Current", "A", int),

        "input_voltage_range": ReadingDefinition(
            15,
            "Input Voltage Range",
            "",
            str,
            description="Options: Appliance / UPS",
        ),

        "output_source_priority": ReadingDefinition(
            16,
            "Output Source Priority",
            "",
            str,
            description=f"Options: {OUTPUT_SOURCE_PRIORITIES}",
        ),

        "charger_source_priority": ReadingDefinition(
            17,
            "Charger Source Priority",
            "",
            str,
            description="Utility first / Solar first / Solar + Utility / Solar only",
        ),

        "max_parallel_units": ReadingDefinition(
            18,
            "Max Parallel Units",
            "",
            str,
            description="May be '-' or unset on some models",
        ),

        "machine_type": ReadingDefinition(
            19,
            "Machine Type",
            "",
            str,
            description="00=Grid tie, 01=Off-grid, 10=Hybrid",
        ),

        "topology": ReadingDefinition(
            20,
            "Topology",
            "",
            str,
            description="transformerless / transformer",
        ),

        "output_mode": ReadingDefinition(
            21,
            "Output Mode",
            "",
            str,
            description=f"Options: {OUTPUT_MODES}",
        ),

        "battery_redischarge_voltage": ReadingDefinition(
            22,
            "Battery Redischarge Voltage",
            "V",
            float,
        ),

        "pv_ok_condition": ReadingDefinition(
            23,
            "PV OK Condition",
            "",
            str,
        ),

        "pv_power_balance": ReadingDefinition(
            24,
            "PV Power Balance",
            "",
            str,
        ),

        "max_cv_charge_time": ReadingDefinition(
            25,
            "Max CV Charge Time",
            "min",
            int,
        ),

        "operation_logic": ReadingDefinition(
            26,
            "Operation Logic",
            "",
            str,
            description="Automatic / On-line / ECO",
        ),
    },
)


PBDV = CommandDefinition(
    id="PBDV",
    title="Battery Re-discharge Voltage",
    description="Set the voltage at which once the battery has recharged to the inverter will re=enable discharging",
    category=CommandCategory.CONFIG_WRITE,

    request=RequestSpec(command="PBDV"),
    response=ResponseSpec(parser=parse_pi30_ascii),

    parameters={"battery_voltage": 
        ParameterSpec(
            name="battery_voltage",
            pattern=re.compile(r"(4[8-9]|5[0-7])\.\d"),
            description="Battery re-discharge voltage", )
    },

    side_effects=True,
)

COMMANDS: dict[str, CommandDefinition] = {
    "QID": QID,
    "QPIGS": QPIGS,
    "QPIRI": QPIRI,
    "QPIWS": QPIWS,
    "PBDV": PBDV,
}

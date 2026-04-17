""" pi30 commands that read identity values (ie ones that identify the device, not its current status) """

from powermon.protocols.model import (
    CommandCategory,
    CommandDefinition,
    ParameterSpec,
    ReadingDefinition,
    RequestSpec,
    ResponseSpec,
)
from powermon.protocols.parsers import parse_pi30_ascii, parse_pi30_flags
from powermon.protocols.transforms import Scale

QID = CommandDefinition(
    command_id="QID",
    name="Serial Number",
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

QPI = CommandDefinition(
    command_id="QPI",
    name="Protocol ID",
    description="Get the Inverter supported Protocol ID",
    category=CommandCategory.IDENTITY,

    request=RequestSpec(command="QPI"),
    response=ResponseSpec(
        parser=parse_pi30_ascii,
        min_fields=1,
        max_fields=1,
    ),

    readings={
        "protocol_id": ReadingDefinition(
            index=0,
            label="Protocol Id",
            unit="",
            dtype=str,
        ),
    },
)

QVFW = CommandDefinition(
    command_id="QVFW",
    name="Main CPU Firmware Version",
    description="Get the Main CPU firmware version",
    category=CommandCategory.IDENTITY,

    request=RequestSpec(command="QVFW"),
    response=ResponseSpec(
        parser=parse_pi30_ascii,
        min_fields=1,
        max_fields=1,
    ),
    readings={
        "main_cpu_firmware_version": ReadingDefinition(
            index=0,
            label="Main CPU Firmware Version",
            unit="",
            dtype=str,
        ),
    },
)
    
QVFW2 = CommandDefinition(
    command_id="QVFW2",
    name="Secondary CPU Firmware Version",
    description="Get the Secondary CPU firmware version",
    category=CommandCategory.IDENTITY,

    request=RequestSpec(command="QVFW2"),
    response=ResponseSpec(
        parser=parse_pi30_ascii,
        min_fields=1,
        max_fields=1,
    ),
    readings={
        "secondary_cpu_firmware_version": ReadingDefinition(
            index=0,
            label="Secondary CPU Firmware Version",
            unit="",
            dtype=float,
            transform=Scale(4)
        ),
    },
)

# "format_template" : "r.removeprefix('VERFW:')"}],
#    "test_responses": [b"(VERFW:00072.70\x53\xA7\r"],


ID_COMMANDS: dict[str, CommandDefinition] = {
    "QID": QID,
    "QPI": QPI,
    "QVFW": QVFW,
    "QVFW2": QVFW2,
}
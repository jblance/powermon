from powermon.protocols.model import (
    CommandCategory,
    CommandDefinition,
    ParameterSpec,
    ReadingDefinition,
    RequestSpec,
    ResponseSpec,
)

from powermon.protocols.parsers import parse_pi30_ascii

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


COMMANDS: dict[str, CommandDefinition] = {
    "QID": QID,
}
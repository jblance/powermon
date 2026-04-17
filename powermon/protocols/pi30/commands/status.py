""" pi30 commands that read status (health, modes, warnings) values """
from powermon.protocols.model import (
    CommandCategory,
    CommandDefinition,
    ParameterSpec,
    ReadingDefinition,
    RequestSpec,
    ResponseSpec,
)
from powermon.protocols.parsers import parse_pi30_ascii, parse_pi30_flags

QPIWS = CommandDefinition(
    command_id="QPIWS",
    name="Warning Status",
    description="Get any active Warning Status flags",
    category=CommandCategory.STATUS,

    request=RequestSpec(command="QPIWS"),
    response=ResponseSpec(
        parser=parse_pi30_flags,
        min_fields=35,
    ),

    readings={
        "pv_loss_warning": ReadingDefinition(index=0, label="PV loss warning", unit="", dtype=bool),
        "battery_low_alarm": ReadingDefinition(index=12, label="Battery low alarm warning", unit="", dtype=bool),
        "battery_equalisation": ReadingDefinition(index=35, label="Battery equalisation warning", unit="", dtype=bool),
    },

)

STATUS_COMMANDS: dict[str, CommandDefinition] = {
    "QPIWS": QPIWS,
}
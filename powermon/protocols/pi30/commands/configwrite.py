""" pi30 commands that write configuration values """
import re

from powermon.protocols.model import (
    CommandCategory,
    CommandDefinition,
    ParameterSpec,
    ReadingDefinition,
    RequestSpec,
    ResponseSpec,
)
from powermon.protocols.parsers import parse_pi30_ascii

PBDV = CommandDefinition(
    command_id="PBDV",
    name="Battery Redischarge Voltage",
    description="Set the voltage at which once the battery has recharged to the inverter will reenable discharging",
    category=CommandCategory.CONFIG_WRITE,

    request=RequestSpec(command="PBDV"),
    response=ResponseSpec(parser=parse_pi30_ascii),

    parameters={"voltage": 
        ParameterSpec(
            name="voltage",
            pattern=re.compile(r"(4[8-9]|5[0-7])\.\d"),
            description="Battery redischarge voltage", )
    },

    side_effects=True,
)

WRITE_COMMANDS: dict[str, CommandDefinition] = {
    "PBDV": PBDV,
}
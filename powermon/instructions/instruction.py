""" commands / command.py """
import logging

from dateparser import parse as dateparse  #noqa:F401

from powermon.commands.command_definition import CommandDefinition
# from powermon.commands.result import Result
# from powermon.exceptions import (
#     CommandExecutionFailed,
#     InvalidCRC,
#     InvalidResponse,
# )

from ._config import InstructionConfig
from ._types import InstructionType
from .outputs import Output
# from .outputs.abstractoutput import AbstractOutput
from .triggers import Trigger

log = logging.getLogger("Instruction")


class Instruction():
    """ class that incapsulates an instruction from the user (ie from config file)
    """

    @staticmethod
    def from_config(config: InstructionConfig) -> "Instruction":
        """build object from config dict"""

        # build trigger
        trigger = Trigger.from_config(config.trigger)

        # build outputs list
        outputs = []
        for output_config in config.outputs:
            outputs.append(Output.from_config(output_config))

        # overrides
        # TODO: implement overrides handling in instruction

        instruction_type: InstructionType = config.type
        # template = None
        match instruction_type:
            case InstructionType.BASIC:
                from .instruction_basic import InstructionBasic as instruction
            case InstructionType.TEMPLATE:
                from .instruction_template import InstructionTemplate as instruction
            case InstructionType.CACHE_QUERY:
                from .instruction_cache_query import InstructionCacheQuery as instruction

        _instruction = instruction(command_str=config.command, trigger=trigger, outputs=outputs, config=config)
        return _instruction


    def __init__(self, command_str: str, trigger: Trigger, outputs: list[Output], config: InstructionConfig):
        self.command_str = command_str
        self.outputs: list[Output] = outputs
        self.trigger: Trigger = trigger

        # self.command_definition: CommandDefinition
        # self.template: str = None
        self.full_command: str = None
        self.override: dict = {}


    def __str__(self):
        _outs = ""
        for output in self.outputs:
            _outs += str(output)

        return f"{self.__class__.__name__}: {self.command_str=}, {self.full_command=}, [{_outs=}], {self.trigger!s}, {self.command_definition!s} {self.override=}"


    # def build_result(self, raw_response=None, protocol=None) -> Result:
    #     """ build a result object from the raw_response """
    #     log.debug("build_result: for command with 'code: %s, command_definition: %s'", self.code, self.command_definition)
    #     try:
    #         # check response is valid
    #         protocol.check_valid(raw_response, self.command_definition)
    #         # check crc is correct
    #         protocol.check_crc(raw_response, self.command_definition)
    #         # trim response
    #         trimmed_response = protocol.trim_response(raw_response, self.command_definition)
    #         # split response
    #         responses = protocol.split_response(trimmed_response, self.command_definition)
    #         # build the Result object
    #         result = Result(command=self, raw_response=raw_response, responses=responses)
    #     except (InvalidResponse, InvalidCRC, CommandExecutionFailed) as e:
    #         result = Result(command=self, raw_response=e, responses=[], is_error=True)
    #     return result

    @property
    def full_command(self) -> str | None:
        """return the full command, including CRC and/or headers"""
        return self._full_command

    @full_command.setter
    def full_command(self, full_command):
        """ store the full command """
        self._full_command = full_command

    def get_command(self):
        return self.command_str

    @property
    def command_definition(self) -> CommandDefinition:
        """ the definition of this command """
        return getattr(self, "_command_definition", None)

    @command_definition.setter
    def command_definition(self, command_definition: CommandDefinition):
        """store the definition of the command"""
        log.debug("Setting command_definition to: %s", command_definition)
        if command_definition is None:
            raise ValueError("CommandDefinition cannot be None")

        # Check if the definition is valid for the command
        # if command_definition.is_command_code_valid(self.code) is False:
        #     raise ValueError(f"Command code {self.code} is not valid for command definition regex {command_definition.regex}")
        self._command_definition = command_definition

    # @property
    # def override(self):
    #     """ dict of override options """
    #     # use getattr and return None if _override not set
    #     return getattr(self, "_override", None)

    # @override.setter
    # def override(self, value):
    #     self._override = value

    @property
    def outputs(self) -> list[Output]:
        """ a list of output objects """
        return self._outputs

    @outputs.setter
    def outputs(self, outputs: list[Output]):
        self._outputs = outputs


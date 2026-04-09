""" commands / command.py """
import logging
from typing import Optional

from dateparser import parse as dateparse # type: ignore[unresolved-import] # noqa: F401

from powermon.commands.command_definition import CommandDefinition
from powermon.commands.result import Result
from powermon.exceptions import (
    CommandExecutionFailed,
    InvalidCRC,
    InvalidResponse,
)

from ._config import ActionConfig
from ._types import ActionType
from .outputs import Output

# from .outputs.abstractoutput import AbstractOutput
from .triggers import Trigger

log = logging.getLogger("Action")


class Action():
    """ class that incapsulates an Action from the user (ie from config file)
    """

    @staticmethod
    def from_config(config: ActionConfig) -> "Action":
        """build object from config dict"""

        # build trigger
        trigger = Trigger.from_config(config.trigger)

        # build outputs list
        outputs = []
        for output_config in config.outputs:
            outputs.append(Output.from_config(output_config))

        # overrides
        # TODO: implement overrides handling in Action

        Action_type: ActionType = config.type
        # template = None
        match Action_type:
            case ActionType.BASIC:
                from .action_basic import ActionBasic as Action
            case ActionType.TEMPLATE:
                from .action_template import ActionTemplate as Action
            case ActionType.CACHE_QUERY:
                from .action_cache_query import ActionCacheQuery as Action

        _Action = Action(command_str=config.command, trigger=trigger, outputs=outputs, config=config)
        return _Action


    def __init__(self, command_str: str, trigger: Trigger, outputs: list[Output], config: ActionConfig):
        self.command_str: str = command_str
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


    def build_result(self, raw_response, protocol) -> Result:
        """ build a result object from the raw_response """
        log.debug("build_result: for command with 'code: %s, command_definition: %s'", self.command_str, self.command_definition)
        try:
            # check response is valid
            protocol.check_valid(raw_response, self.command_definition)
            # check crc is correct
            protocol.check_crc(raw_response, self.command_definition)
            # trim response
            trimmed_response = protocol.trim_response(raw_response, self.command_definition)
            # split response
            responses = protocol.split_response(trimmed_response, self.command_definition)
            # build the Result object
            result = Result(command=self, raw_response=raw_response, responses=responses)
        except (InvalidResponse, InvalidCRC, CommandExecutionFailed) as e:
            result = Result(command=self, raw_response=e, responses=[], is_error=True)
        return result

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
    def command_definition(self) -> Optional[CommandDefinition]:
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


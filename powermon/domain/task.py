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

from . import TaskConfig
from .domain_types import TaskType
from powermon.outputs import Output

# from .outputs.abstractoutput import AbstractOutput
from .triggers import Trigger

log = logging.getLogger("Task")


class Task():
    """ class that incapsulates a Task from the user (ie from config file)
    """

    @staticmethod
    def from_config(config: TaskConfig) -> "Task":
        """build object from config dict"""

        # build trigger
        trigger = Trigger.from_config(config.trigger)

        # build outputs list
        outputs = []
        for output_config in config.outputs:
            outputs.append(Output.from_config(output_config))

        # overrides
        # TODO: implement overrides handling in Task

        task_type: TaskType = config.type
        # template = None
        match task_type:
            case TaskType.BASIC:
                from .task_basic import TaskBasic as Task
            case TaskType.TEMPLATE:
                from .task_template import TaskTemplate as Task
            case TaskType.CACHE_QUERY:
                from .task_cache_query import TaskCacheQuery as Task

        _task = Task(command_str=config.command, trigger=trigger, outputs=outputs, config=config)
        return _task


    def __init__(self, command_str: str, trigger: Trigger, outputs: list[Output], config: TaskConfig):
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


class TaskTemplate(Task):
    pass

    def get_command(self):
        try:
            _command = eval(self.command_str)
            log.debug("eval'd command_str to %s", _command)
            return _command
        except SyntaxError as ex:
            print(ex)
            return
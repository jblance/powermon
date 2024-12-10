""" commands / command_definition.py """
import logging
import re
from enum import StrEnum, auto

import construct as cs
from pydantic import BaseModel

from powermon.commands.reading_definition import ReadingDefinition, ReadingType
from powermon.commands.result import ResponseType, ResultType

log = logging.getLogger("CommandDefinition")


class CommandCategory(StrEnum):
    """ enum of command categories """
    CONFIG = auto()
    INFO = auto()
    SETTINGS = auto()
    DEFAULTS = auto()
    DATA = auto()


class CommandDefinitionDTO(BaseModel):
    """ model/allowed elements for a CommandDefinition data transfer object """
    code: str
    description: str
    help_text: str | None
    result_type: str | None
    command_type: str | None
    command_code: str | int | None
    command_data: str | int | None
    construct_txt: None | str
    construct_min_response: None | int
    reading_definitions: list
    test_responses: list[bytes] | None
    regex: str | None
    aliases: str | None


class CommandDefinition:
    """ object the contains the definition and other metadata about a command, including:
    - code
    - regex (opt)
    - description
    - result type
    - reading definitions
    - test responses
    """
    def __str__(self):
        return f"CommandDefinition: {self.code=}, {self.description=}, {self.result_type=}, reading_definition count: {self.reading_definition_count()}, {self.command_code=}, {self.command_type=}, {self.command_data=}, {self.category=}"

    def __init__(self, code, description, help_text: str, result_type : ResultType, reading_definitions, test_responses: list = None, regex: str = None):
        """ init CommandDefinition class """
        if reading_definitions is None or len(reading_definitions) == 0:
            raise ValueError(f"reading definitions cannot be None for command_code: {code}")

        self.code = code
        self.description = description
        self.help_text = help_text
        self.result_type: ResultType = result_type
        self.reading_definitions: dict[int | str, ReadingDefinition] = reading_definitions
        self.test_responses: list[bytes] = test_responses
        self.regex: str | None = regex
        self.aliases: str = None
        self.category = None
        self.command_type = None
        self.command_code: str = None
        self.command_data: str = None
        self.construct: cs.Construct = None
        self.construct_min_response: int = 0
        self.match = None

    def to_dto(self) -> CommandDefinitionDTO:
        """ convert command definition object to data transfer object """
        return CommandDefinitionDTO(
            code=self.code,
            description=self.description,
            help_text=self.help_text,
            result_type=str(self.result_type),
            aliases=self.aliases,
            command_type=self.command_type,
            command_code=self.command_code,
            command_data=self.command_data,
            construct_txt=self.construct,
            construct_min_response=self.construct_min_response,
            reading_definitions=self.reading_definitions,
            test_responses=self.test_responses,
            regex=self.regex
        )

    @property
    def help_text(self):
        if self._help_text is None:
            return ""
        return self._help_text

    @help_text.setter
    def help_text(self, value):
        self._help_text = value

    @property
    def aliases(self):
        if self._aliases is None:
            return ""
        return self._aliases

    @aliases.setter
    def aliases(self, value):
        self._aliases = value

    @classmethod
    def from_config(cls, protocol_dictionary : dict) -> "CommandDefinition":
        """ build command definition object from config dict """
        # log.debug("command definition: %s", protocol_dictionary)
        code = protocol_dictionary.get("name")
        description = protocol_dictionary.get("description")
        help_text = protocol_dictionary.get("help")
        test_responses = protocol_dictionary.get("test_responses")
        regex = protocol_dictionary.get("regex", None)
        result_type = protocol_dictionary.get("result_type")
        match result_type:
            case ResultType.ACK:
                # All ResultType.ACK are the same, so put config here instead of duplicating it in the protocol
                log.debug("ResultType.ACK so defaulting reading_definitions")
                reading_definitions : dict[int, ReadingDefinition] = \
                    ReadingDefinition.multiple_from_config([{"description": description, "response_type": ResponseType.ACK, "reading_type": ReadingType.ACK}])
                test_responses = [b"(NAK\x73\x73\r", b"(ACK\x39\x20\r",]
            case ResultType.PI18_ACK:
                # All ResultType.PI18_ACK are the same, so put config here instead of duplicating it in the protocol
                log.debug("ResultType.PI18_ACK so defaulting reading_definitions")
                reading_definitions : dict[int, ReadingDefinition] = \
                    ReadingDefinition.multiple_from_config([{"description": description, "response_type": ResponseType.ACK, "reading_type": ReadingType.PI18_ACK}])
                test_responses = [b"^0\x1b\xe3\r", b"^1\x0b\xc2\r",]
            case _:
                reading_definitions : dict[int, ReadingDefinition] = \
                    ReadingDefinition.multiple_from_config(protocol_dictionary.get("reading_definitions"))

        log.debug("code: %s description: '%s' with %s reading_definitions", code, description, len(reading_definitions))
        _command_definition = cls(
            code=code, description=description, help_text=help_text, result_type=result_type,
            reading_definitions=reading_definitions, test_responses=test_responses,
            regex=regex
        )
        _command_definition.aliases = protocol_dictionary.get("aliases")
        _command_definition.category = protocol_dictionary.get("category", CommandCategory.DATA)
        _command_definition.command_type = protocol_dictionary.get("command_type")
        _command_definition.command_code = protocol_dictionary.get("command_code")
        _command_definition.command_data = protocol_dictionary.get("command_data")
        _command_definition.construct = protocol_dictionary.get("construct")
        _command_definition.construct_min_response = protocol_dictionary.get("construct_min_response", 8)
        _command_definition.match = None
        return _command_definition

    def is_command_code_valid(self, command_code : str) -> bool:
        """ determines if a command code is valid """
        if self.regex is not None:
            return re.match(self.regex, command_code) is not None
        if self.aliases is not None and command_code in self.aliases:
            return True
        return self.code == command_code

    def get_reading_definition(self, lookup=None, position=0) -> ReadingDefinition:
        """ return the reading definition that corresponds to lookup """
        log.debug("looking for reading definition with: %s, result_type is: %s", lookup, self.result_type)
        if self.reading_definitions is None:
            result = None
        match self.result_type:
            case ResultType.ACK | ResultType.PI18_ACK | ResultType.SINGLE | ResultType.MULTIVALUED:
                result = self.reading_definitions[0]
            case ResultType.ORDERED | ResultType.SLICED | ResultType.COMMA_DELIMITED:
                result = self.reading_definitions[position]
            case ResultType.VED_INDEXED | ResultType.CONSTRUCT | ResultType.BYTEARRAY:
                try:
                    result = self.reading_definitions[lookup]
                except KeyError:
                    log.debug("no reading definition found for key: %s", lookup)
                    # print(f"command_definition@106:no reading definition found for key: {lookup}")
                    result = None
            case _:
                print(f"command_definition@139: no get_reading_definition for {self.result_type=}")
                exit()
        log.debug("found reading definition: %s", result)
        return result

    def reading_definition_count(self) -> int:
        """ return the number of reading_definitions for this command_definition """
        return 0 if self.reading_definitions is None else len(self.reading_definitions)

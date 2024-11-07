""" testport.py """
import logging
import random

from powermon.commands.command import Command
from powermon.commands.command_definition import CommandDefinition
from powermon.commands.result import Result
from powermon.ports import PortType
# from powermon.dto.portDTO import PortDTO
from powermon.ports.abstractport import AbstractPort, _AbstractPortDTO
from powermon.protocols import get_protocol_definition

log = logging.getLogger("test")


class TestPortDTO(_AbstractPortDTO):
    """ data transfer model for TestPort class """
    response_number: None | int


class TestPort(AbstractPort):
    """ test port object - responds with test data (if configured in the protocol) """
    def __init__(self, response_number, protocol):
        self.port_type = PortType.TEST
        super().__init__(protocol=protocol)

        self.response_number = response_number
        self.connected = False
        self._test_data = None

    def to_dto(self) -> _AbstractPortDTO:
        dto = TestPortDTO(port_type=self.port_type, protocol=self.protocol.to_dto(), response_number=self.response_number)
        return dto

    def __str__(self):
        return "Test port"

    @classmethod
    async def from_config(cls, config=None):
        log.debug("building test port. config:%s", config)
        # allows specification of which of the test responses to use (mainly to allow test cases to be repeatable)
        response_number = config.get("response_number", None)
        # get protocol handler, default to PI30 if not supplied
        protocol = get_protocol_definition(protocol=config.get("protocol", "PI30"))
        return cls(response_number=response_number, protocol=protocol)

    def is_connected(self):
        log.debug("Test port is connected")
        return True

    async def connect(self) -> int:
        log.debug("Test port connected")
        self.connected = True
        return 1

    async def disconnect(self) -> None:
        log.debug("Test port disconnected")
        self.connected = False

    async def send_and_receive(self, command: Command) -> Result:
        full_command = command.full_command
        log.info("Executing command via testport: %s", full_command)

        command_defn : CommandDefinition = command.command_definition
        if command_defn is not None:
            # Have test data defined, so use that
            number_of_test_responses = len(command_defn.test_responses)
            if self.response_number is not None and self.response_number < number_of_test_responses:
                self._test_data = command_defn.test_responses[self.response_number]
                log.info('Selected response number %s:, %s', self.response_number, self._test_data)
            else:
                self._test_data = command_defn.test_responses[random.randrange(number_of_test_responses)]
                log.info('Applying random response: %s', self._test_data)
        else:
            # No test responses defined
            raise ValueError(f"Testing a command '{command.code}' with no test responses defined")
        
        # Get raw response
        response_line = self._test_data
        log.debug("Raw response: %s", response_line)

        # response = self.get_protocol().check_response_and_trim(response_line)
        result = command.build_result(raw_response=response_line, protocol=self.protocol)
        return result

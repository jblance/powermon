""" testport.py """
import logging
import random

# from powermon.commands.command import Command
from powermon.commands.command_definition import CommandDefinition
from powermon.commands.result import Result
from ._types import PortType
from .port import Port
from ...actions import Action

log = logging.getLogger("test")


class TestPort(Port):
    """ test port object - responds with test data (if configured in the protocol) """
    def __init__(self, response_number, protocol):
        self.port_type = PortType.TEST
        super().__init__(protocol=protocol)

        self.response_number = response_number
        self.connected = False
        # self._test_data = None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.response_number=}"

    def __repr__(self) -> str:
        """ Returns representation of the port that allows eval(port.__repr__()) to rebuild object"""
        return f"TestPort(response_number='{self.response_number}', protocol='{self.protocol.protocol_id}')"

    @classmethod
    async def from_config(cls, config, protocol, serial_number) -> "TestPort":
        log.debug("building test port. config:%s", config)
        return cls(response_number=config.response_number, protocol=protocol)

    def is_connected(self) -> bool:
        log.debug("Test port is connected")
        return True

    async def connect(self) -> None:
        log.debug("Test port connected")
        self.connected = True
        # return 1

    async def disconnect(self) -> None:
        log.debug("Test port disconnected")
        self.connected = False

    async def get_response(self, action: Action) -> bytes:
        full_command = action.full_command
        log.info("Executing command via testport: %s", full_command)

        command_defn : CommandDefinition = action.command_definition
        if command_defn is not None:
            # Have test data defined, so use that
            number_of_test_responses = len(command_defn.test_responses)
            if self.response_number is not None and self.response_number < number_of_test_responses:
                _test_data = command_defn.test_responses[self.response_number]
                log.info('Selected response number %s:, %s', self.response_number, _test_data)
            else:
                _test_data = command_defn.test_responses[random.randrange(number_of_test_responses)]
                log.info('Applying random response: %s', _test_data)
        else:
            # No test responses defined
            raise ValueError(f"Testing a command '{action.command_str}' with no test responses defined")

        # Get raw response
        log.debug("Raw response: %s", _test_data)
        return _test_data

    # async def send_and_receive(self, action) -> Result:
    #     full_command = action.full_command
    #     log.info("Executing command via testport: %s", full_command)

    #     command_defn : CommandDefinition = action.command_definition
    #     if command_defn is not None:
    #         # Have test data defined, so use that
    #         number_of_test_responses = len(command_defn.test_responses)
    #         if self.response_number is not None and self.response_number < number_of_test_responses:
    #             _test_data = command_defn.test_responses[self.response_number]
    #             log.info('Selected response number %s:, %s', self.response_number, _test_data)
    #         else:
    #             _test_data = command_defn.test_responses[random.randrange(number_of_test_responses)]
    #             log.info('Applying random response: %s', _test_data)
    #     else:
    #         # No test responses defined
    #         raise ValueError(f"Testing a command '{action.command_str}' with no test responses defined")

    #     # Get raw response
    #     log.debug("Raw response: %s", _test_data)
    #     result = action.build_result(raw_response=_test_data, protocol=self.protocol)
    #     return result

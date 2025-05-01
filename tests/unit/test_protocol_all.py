import unittest

from powermon.commands.command import Command
from powermon.libs.errors import CommandDefinitionMissing
from powermon.protocols import Protocol
from powermon.protocols import from_name as get_protocol_definition
from powermon.protocols.abstractprotocol import AbstractProtocol

PROTOCOLS_TO_SKIP_FOR_GET_ID = [Protocol.DALY, Protocol.NEEY, Protocol.HELTEC, Protocol.JKSERIAL]  # TODO: see if there are get_id commands for these protocols

class TestProtocolAll(unittest.TestCase):
    """ do simple tests for all protocols """
    def test_check_default_command(self):
        """ test a for default command in each protocol """
        for protocol in Protocol:
            proto = get_protocol_definition(name=protocol)
            try:
                proto.get_command_definition(command='default')
                self.assertIsInstance(proto, AbstractProtocol)
            except CommandDefinitionMissing:
                self.fail(f"no default command for {protocol}")


    def test_get_id_command(self):
        """ test get_id works for each protocol """
        for protocol in Protocol:
            if protocol in PROTOCOLS_TO_SKIP_FOR_GET_ID:
                continue
            proto = get_protocol_definition(name=protocol)
            # print(protocol, proto)
            try:
                command = proto.get_id_command()
                self.assertIsInstance(command, Command)
            except CommandDefinitionMissing:
                self.fail(f"no get_id command for {protocol}")
                # print(command)

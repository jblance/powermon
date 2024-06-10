""" tests / pmon / unit / test_protocol_pi18.py """
import unittest
from powermon.protocols.pi18 import PI18 as Proto

proto = Proto()


class TestProtocolPI18(unittest.TestCase):
    """ exercise different functions in jkserial protocol """

    def test_check_crc_good(self):
        """ test a for correct CRC validation """
        response = b"^D0882300,217,2300,500,217,5000,5000,480,480,530,440,570,570,2,10,070,1,1,1,9,0,0,0,0,1,00\xe1k\r"
        result = proto.check_crc(response=response, command_definition=proto.get_command_definition('PIRI'))
        self.assertTrue(result)

    def test_check_crc_incorrect(self):
        """ test a for failing CRC validation (crc is wrong) """
        response = b"^D0882300,217,2300,500,217,5000,5000,480,480,530,440,570,570,2,10,070,1,1,1,9,0,0,0,0,1,00\xe2k\r"
        result = proto.check_crc(response=response, command_definition=proto.get_command_definition('PIRI'))
        self.assertFalse(result)

    def test_check_crc_wrong_response_start(self):
        """ test a for failing CRC validation (not a response that starts with ^D) """
        response = b"0882300,217,2300,500,217,5000,5000,480,480,530,440,570,570,2,10,070,1,1,1,9,0,0,0,0,1,00\xe1k\r"
        result = proto.check_crc(response=response, command_definition=proto.get_command_definition('PIRI'))
        self.assertFalse(result)

    def test_get_full_command_piri(self):
        """ test full command generation for PIRI command """
        fc = proto.get_full_command('PIRI')
        # print(fc)
        expected = b'^P007PIRI\xee8\r'
        self.assertEqual(expected, fc)

    def test_get_full_command_pi(self):
        """ test full command generation for PI command """
        fc = proto.get_full_command('PI')
        # print(fc)
        expected = b'^P005PIq\x8b\r'
        self.assertEqual(expected, fc)

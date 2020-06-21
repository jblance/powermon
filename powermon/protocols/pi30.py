import logging

from .protocol import AbstractProtocol

log = logging.getLogger('powermon')

COMMANDS = [
    {
        "name": "QPI",
        "description": "Protocol ID inquiry",
        "help": " -- queries the device protocol ID. e.g. 30 for HS series",
        "type": "QUERY",
        "response": [
            ["string", "Protocol ID", ""]
        ],
        "test_responses": [
            ["(PI30", "9A0B"]
        ],
        "regex": ""
    },
    {
        "name": "QPIGS",
        "description": "General Status Parameters inquiry",
        "help": " -- queries the value of various metrics from the Inverter",
        "type": "QUERY",
        "response": [
            ["float", "AC Input Voltage", "V"],
            ["float", "AC Input Frequency", "Hz"],
            ["float", "AC Output Voltage", "V"],
            ["float", "AC Output Frequency", "Hz"],
            ["int", "AC Output Apparent Power", "VA"],
            ["int", "AC Output Active Power", "W"],
            ["int", "AC Output Load", "%"],
            ["int", "BUS Voltage", "V"],
            ["float", "Battery Voltage", "V"],
            ["int", "Battery Charging Current", "A"],
            ["int", "Battery Capacity", "%"],
            ["int", "Inverter Heat Sink Temperature", "Deg_C"],
            ["float", "PV Input Current for Battery", "A"],
            ["float", "PV Input Voltage", "V"],
            ["float", "Battery Voltage from SCC", "V"],
            ["int", "Battery Discharge Current", "A"],
            ["flags", "Device Status", [
                "is_sbu_priority_version_added",
                "is_configuration_changed",
                "is_scc_firmware_updated",
                "is_load_on",
                "is_battery_voltage_to_steady_while_charging",
                "is_charging_on",
                "is_scc_charging_on",
                "is_ac_charging_on"]
             ],
            ["int", "RSV1", "A"],
            ["int", "RSV2", "A"],
            ["int", "PV Input Power", "W"],
            ["flags", "Device Status2", [
                "is_charging_to_float",
                "is_switched_on",
                "is_reserved"]
             ]],
        "test_responses": [
            ["(000.0 00.0 230.0 49.9 0161 0119 003 460 57.50 012 100 0069 0014 103.8 57.45 00000 00110110 00 00 00856 010", "248C"]
        ],
        "regex": ""
    }
]


class pi30(AbstractProtocol):
    def __init__(self, *args, **kwargs) -> None:
        self._protocol_id = 'PI30'
        log.info(f'Using protocol {self._protocol_id}')
        self.__command = None

    def get_protocol_id(self):
        return self._protocol_id

    def set_command(self, command):
        self.__command = command

    def is_known_command(self) -> bool:
        if self.__command is None:
            log.info('is_known_command called with self._current_command = None')
            return False
        for _command in COMMANDS:
            print(f'_command {_command}')
        return True
        # else:
        #    return False

    def get_full_command(self) -> bytes:
        byte_cmd = bytes(self.__command, 'utf-8')
        # calculate the CRC
        crc_high, crc_low = self.crc(byte_cmd)
        # combine byte_cmd, CRC , return
        full_command = byte_cmd + bytes([crc_high, crc_low, 13])
        log.debug('full command: %s', full_command)
        return full_command

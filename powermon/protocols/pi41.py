import logging

from .pi30 import pi30

log = logging.getLogger('powermon')

NEW_COMMANDS = {
    'QP2GS': {
        "name": "QP2GS",
        "description": "Parallel Information inquiry",
        "help": " -- example: QP2GS1 queries the values of various metrics from instance 1 of parallel setup Inverters (numbers from 0)",
        "type": "QUERY",
        "response": [
            ["int", "Parallel instance number??", ""],
            ["int", "Serial number", ""],
            ["keyed", "Work mode", {"P": "Power On Mode",
                                    "S": "Standby Mode",
                                    "L": "Line Mode",
                                    "B": "Battery Mode",
                                    "F": "Fault Mode",
                                    "H": "Power Saving Mode"}],
            ["keyed", "Fault code", {"00": "No fault",
                                     "01": "Fan is locked",
                                     "02": "Over temperature",
                                     "03": "Battery voltage is too high",
                                     "04": "Battery voltage is too low",
                                     "05": "Output short circuited or Over temperature",
                                     "06": "Output voltage is too high",
                                     "07": "Over load time out",
                                     "08": "Bus voltage is too high",
                                     "09": "Bus soft start failed",
                                     "11": "Main relay failed",
                                     "51": "Over current inverter",
                                     "52": "Bus soft start failed",
                                     "53": "Inverter soft start failed",
                                     "54": "Self-test failed",
                                     "55": "Over DC voltage on output of inverter",
                                     "56": "Battery connection is open",
                                     "57": "Current sensor failed",
                                     "58": "Output voltage is too low",
                                     "60": "Inverter negative power",
                                     "71": "Parallel version different",
                                     "72": "Output circuit failed",
                                     "80": "CAN communication failed",
                                     "81": "Parallel host line lost",
                                     "82": "Parallel synchronized signal lost",
                                     "83": "Parallel battery voltage detect different",
                                     "84": "Parallel Line voltage or frequency detect different",
                                     "85": "Parallel Line input current unbalanced",
                                     "86": "Parallel output setting different"}],
            ["float", "L2 AC input voltage", "V"],
            ["float", "L2 AC input frequency", "Hz"],
            ["float", "L2 AC output voltage", "V"],
            ["float", "L2 AC output frequency", "Hz"],
            ["int", "L2 AC output apparent power", "VA"],
            ["int", "L2 AC output active power", "W"],
            ["int", "L2 Load percentage", "%"],
            ["float", "L2 Battery voltage", "V"],
            ["int", "L2 Battery charging current", "A"],
            ["int", "L2 Battery capacity", "%"],
            ["float", "PV2 Input Voltage", "V"],
            ["int", "PV2 charging current", "A"],
            ["flags", "Inverter Status", [
                "is_l2_scc_ok",
                "is_l2_ac_charging",
                "is_l2_scc_charging",
                "is_battery_over_voltage",
                "is_battery_under_voltage",
                "is_l2_line_lost",
                "is_l2_load_on",
                "is_configuration_changed"]]
        ],
        "test_responses": [
            b"(11 92911906100045 L 00 124.2 59.98 124.2 59.98 0149 0130 005 56.1 000 100 000.0 00 01000010\xA9\xA8\r",
        ],
        "regex": "QP2GS(\\d)$"
    },
}


class pi41(pi30):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self._protocol_id = b'PI41'
        self.COMMANDS.append(NEW_COMMANDS)
        # log.info(f'Using protocol {self._protocol_id} with {len(self.COMMANDS)} commands')

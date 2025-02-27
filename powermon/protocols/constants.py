""" protocol constants """
BATTERY_TYPES = [
    "AGM",
    "Flooded",
    "User",
    "Pylontech",
    "Shinheung",
    "WECO",
    "Soltaro",
    "TBD",
    "LIb-protocol compatible",
    "3rd party Lithium"
]

CHARGER_SOURCE_PRIORITIES = [
    "Utility first",
    "Solar first",
    "Solar + Utility",
    "Solar only"
]

OUTPUT_MODES = [
    "single machine",
    "parallel",
    "Phase 1 of 3 phase",
    "Phase 2 of 3 phase",
    "Phase 3 of 3 phase",
    "Phase 1 of 2 phase",
    "Phase 2 of 2 phase"
]

PI30_OUTPUT_MODES = OUTPUT_MODES.copy()
PI30_OUTPUT_MODES[6] = "Phase 2 of 2 phase (120°)"
PI30_OUTPUT_MODES.append("Phase 2 of 2 phase (180°)")

OUTPUT_SOURCE_PRIORITIES = [
    "Utility > Solar > Battery",
    "Solar > Utility > Battery",
    "Solar > Battery > Utility"
]

INVERTER_MODE_OPTIONS = {
    "P": "Power on",
    "S": "Standby",
    "L": "Line",
    "B": "Battery",
    "F": "Fault",
    "H": "Power Saving",
    "D": "Shutdown",
    "Y": "Bypass"
}

# Legacy Priorities List
OUTPUT_SOURCE_PRIORITIES_PI30MAX =  [
    "Utility first", 
    "Solar first", 
    "SBU first"
]

FAULT_CODE_OPTIONS = {
    "00": "No fault",
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
    "86": "Parallel output setting different"}


FAULT_CODE_OPTIONS_PI30MAX = {
    "00": "No fault",
    "01": "Fan is locked",
    "02": "Over temperature",
    "03": "Battery voltage is too high",
    "04": "Battery voltage is too low",
    "05": "Output short circuited or Over temperature",
    "06": "Output voltage is too high",
    "07": "Over load time out",
    "08": "Bus voltage is too high",
    "09": "Bus soft start failed",
    "10": "PV over current",
    "11": "PV over voltage",
    "12": "DC over current",
    "13": "Battery discharge over current",
    "51": "Over current inverter",
    "52": "Bus voltage too low",
    "53": "Inverter soft start failed",
    "54": "Self-test failed",
    "55": "Over DC voltage on output of inverter",
    "56": "Battery connection is open",
    "57": "Current sensor failed",
    "58": "Output voltage is too low",
    "60": "Power feedback protection",
    "71": "Firmware version different",
    "72": "Current sharing fault",
    "80": "CAN communication failed",
    "81": "Parallel host line lost",
    "82": "Parallel synchronized signal lost",
    "83": "Parallel battery voltage detect different",
    "84": "AC input voltage or frequency detected different",
    "85": "AC output current unbalanced",
    "86": "AC output mode setting different"}

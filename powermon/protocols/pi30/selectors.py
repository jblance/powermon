"""selectors are aliases to a full command 
    or to a single reading in a multiple response command
"""

from powermon.protocols.model import SelectorTarget

SELECTORS = {
    "qid": SelectorTarget("QID"),
    "serial_number": SelectorTarget("QID", reading_key="serial_number"),

    "status": SelectorTarget("QPIGS"),
    "battery_voltage": SelectorTarget("QPIGS", reading_key="battery_voltage"),

    "warnings": SelectorTarget("QPIWS"),

    "re-discharge_voltage": SelectorTarget("PBDV", parameter="voltage"),

    "settings": SelectorTarget("QPIRI"),
    "get_settings": SelectorTarget("QPIRI"),
    "battery_type": SelectorTarget("QPIRI", reading_key="battery_type"),
}
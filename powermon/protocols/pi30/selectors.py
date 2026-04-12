from powermon.protocols.model import SelectorTarget

SELECTORS = {
    "qid": SelectorTarget("QID"),
    "serial_number": SelectorTarget("QID", reading_key="serial_number"),

    "status": SelectorTarget("QPIGS"),
    "battery_voltage": SelectorTarget("QPIGS", reading_key="battery_voltage"),

    "warnings": SelectorTarget("QPIWS"),

    "discharge_voltage": SelectorTarget("PBDV", parameter="battery_voltage"),

    "settings": SelectorTarget("QPIRI"),
    "battery_type": SelectorTarget("QPIRI", reading_key="battery_type"),
}
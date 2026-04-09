""" pi30mst.py """
import logging

from powermon.commands.command_definition import CommandCategory
from powermon.commands.reading_definition import ReadingType, ResponseType
from powermon.commands.result import ResultType
from powermon.protocols.pi30max import PI30MAX


log = logging.getLogger("pi30mst")

# MST variation of QPIGS2
MST_QPIGS2 = {
        "name": "QPIGS2",
        "description": "Get the current values of various General Status parameters 2",
        "category": CommandCategory.DATA,
        "result_type": ResultType.ORDERED,
        "reading_definitions": [
            {"description": "PV2 Input Current",
                "reading_type": ReadingType.CURRENT, "icon": "mdi:solar-power", "device_class": "current", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "PV2 Input Voltage",
                "reading_type": ReadingType.VOLTS, "icon": "mdi:solar-power", "device_class": "voltage", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "Battery voltage from SCC 2",
                "reading_type": ReadingType.VOLTS, "icon": "mdi:solar-power", "device_class": "voltage", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "PV2 Charging Power",
                "reading_type": ReadingType.WATTS, "icon": "mdi:solar-power", "device_class": "power", "state_class": "measurement",
                "response_type": ResponseType.INT},
            {"description": "Device status", "reading_type": ReadingType.MESSAGE,},
            {"description": "AC charging current",
                "reading_type": ReadingType.CURRENT, "icon": "mdi:transmission-tower-export", "device_class": "current", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "AC charging power",
                "reading_type": ReadingType.WATTS, "icon": "mdi:transmission-tower-export", "device_class": "power", "state_class": "measurement",
                "response_type": ResponseType.INT},
            {"description": "PV3 Input Current",
                "reading_type": ReadingType.CURRENT, "icon": "mdi:solar-power", "device_class": "current", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "PV3 Input Voltage",
                "reading_type": ReadingType.VOLTS, "icon": "mdi:solar-power", "device_class": "voltage", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "Battery voltage from SCC 3",
                "reading_type": ReadingType.VOLTS, "icon": "mdi:solar-power", "device_class": "voltage", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "PV3 Charging Power",
                "reading_type": ReadingType.WATTS, "icon": "mdi:solar-power", "device_class": "power", "state_class": "measurement",
                "response_type": ResponseType.INT},
            {"description": "PV total charging power",
                "reading_type": ReadingType.WATTS, "icon": "mdi:solar-power", "device_class": "power", "state_class": "measurement",
                "response_type": ResponseType.INT},
        ],
        "test_responses": [
            b"(03.1 327.3 52.3 123 1 1234 122 327.1 52.4 234 567 \x23\xc7\r",
        ], }


class PI30MST(PI30MAX):
    """ pi30 protocol handler """
    def __str__(self):
        return self.description

    def __init__(self, model=None) -> None:
        super().__init__(model=model)
        self.protocol_id = b"PI30MST"
        self.description = "PI30 protocol handler for PIP4048MST and similar inverters"
        # self.add_command_definitions(QUERY_COMMANDS)

        # Update QPIGS2 to MST definition
        self.replace_command_definition("QPIGS2", MST_QPIGS2)
        self.check_definitions_count(expected=68)

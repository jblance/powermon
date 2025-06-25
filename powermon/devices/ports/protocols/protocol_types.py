from enum import StrEnum, auto

class ProtocolType(StrEnum):
    """Enumeration of currently implemented Protocols"""
    PI18 = auto()  # WIP
    PI30 = auto()
    PI30MAX = auto()
    PI30MST = auto()
    DALY = auto()
    NEEY = auto()
    HELTEC = auto()
    VED = auto()
    JKSERIAL = auto()

from enum import StrEnum, auto

class FormatterType(StrEnum):
    """ enumeration of valid formatter types """
    HASS = auto()
    HASS_AUTODISCOVERY = auto()
    HASS_STATE = auto()
    HTMLTABLE = auto()
    JSON = auto()
    RAW = auto()
    SIMPLE = auto()
    TABLE = auto()
    # TOPICS = auto()
    BMSRESPONSE = auto()
    CACHE = auto()

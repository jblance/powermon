""" outputformats / __init__.py """
import logging
from enum import StrEnum, auto

from rich import print

from powermon.libs.errors import ConfigError

from .abstractformat import AbstractFormat

log = logging.getLogger("formats")


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


DEFAULT_FORMAT = FormatterType.SIMPLE

def list_formats():
    print("[orange]Available output formats")
    for formatter in FormatterType:
        print(f"[green]{formatter.upper()}[/]: {get_formatter(formatter)({})}")
        # print(formatter)


def get_formatter(format_type):
    match format_type:
        case FormatterType.HTMLTABLE:
            from .htmltable import HtmlTable as fmt
        case FormatterType.HASS:
            from .hass import Hass as fmt
        case FormatterType.HASS_AUTODISCOVERY:
            from .hass import HassAutoDiscovery as fmt
        case FormatterType.HASS_STATE:
            from .hass import HassState as fmt
        case FormatterType.JSON:
            from .json_fmt import Json as fmt
        # case FormatterType.TOPICS:
        #     from powermon.outputformats.topics import Topics as fmt
        case FormatterType.SIMPLE:
            from .simple import SimpleFormat as fmt
        case FormatterType.TABLE:
            from .table import Table as fmt
        case FormatterType.RAW:
            from .raw import Raw as fmt
        case FormatterType.CACHE:
            from .cache import Cache as fmt
        case FormatterType.BMSRESPONSE:
            from .bmsresponse import BMSResponse as fmt
        case _:
            log.warning("No formatter found for: %s", format_type)
            return None
    return fmt


def from_config(format_config) -> AbstractFormat:
    """ use a config dict to build and return a format class """
    # Get values from config
    log.debug("Format from_config, format_config: %s", format_config)

    # formatConfig can be None, a str (eg 'simple') or a dict
    if format_config is None:
        format_type = FormatterType.SIMPLE
        format_config = {}
    elif isinstance(format_config, str):
        format_type = format_config
        format_config = {}
        format_config["type"] = format_type
    else:
        format_type = format_config.get("type")
    log.debug("getFormatfromConfig, formatType: %s", format_type)

    fmt = get_formatter(format_type)
    if fmt is None:
        raise ConfigError(f"Unknown formater: {format_type}", format_type)
    return fmt(format_config)

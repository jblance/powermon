""" outputformats / __init__.py """
import logging

from rich import print

from powermon.exceptions import ConfigError

from ._types import FormatterType
from .abstractformat import AbstractFormat

log = logging.getLogger("formats")


class Formatter():
    DEFAULT_FORMAT = FormatterType.SIMPLE

    @staticmethod
    def list_formats():
        print("[orange]Available output formats")
        for formatter in FormatterType:
            print(f"[green]{formatter.upper()}[/]: {Formatter.get_formatter(formatter)({})}")
            # print(formatter)

    @staticmethod
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

    @staticmethod
    def from_config(format_config) -> AbstractFormat:
        """ use a config dict to build and return a format class """
        # Get values from config
        log.debug("format_config: %s", format_config)
        log.debug("formatType: %s", format_config.type)

        fmt = Formatter.get_formatter(format_config.type)
        if fmt is None:
            raise ConfigError(f"Unknown formater: {format_config.type}")
        return fmt(format_config)

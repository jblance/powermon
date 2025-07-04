import logging
from abc import abstractmethod

from rich import print as rprint

# from pydantic import BaseModel
from powermon.commands.result import Result

from ._types import OutputType
from .formatters import Formatter
from .formatters.abstractformat import AbstractFormat

# Set-up logger
log = logging.getLogger("outputs")


class Output():
    """ base class for all output modules """
    @staticmethod
    def get_output_class(output_type, formatter, output_config=None):
        """ return the instantiated output class - inc formatter """
        output_class = None
        # Only import the required class
        log.debug("outputType %s", output_type)
        if output_type == OutputType.MQTT:
            from .mqtt import MQTT
            output_class = MQTT.from_config(output_config)
            output_class.formatter = formatter
        else:
            from .screen import Screen
            output_class = Screen.from_config(output_config)
            output_class.formatter = formatter
        return output_class

    @staticmethod
    def list_outputs():
        """ helper function to display the list of outputs """
        print("Supported outputs")
        for name in OutputType:
            try:
                output = Output.get_output_class(name, Output.DEFAULT, {})
                if output is not None:
                    rprint(f"[GREEN]{name.upper()}[/]: {output}")
            except ModuleNotFoundError as exc:
                log.info("Error in module %s: %s", name, exc)
                continue
            except AttributeError as exc:
                log.info("Error in module %s: %s", name, exc)
                continue

    @staticmethod
    def from_config(output_config):
        """ return output class from a config """
        _outputs = []

        log.debug("parse_output_config, config: %s", output_config)
        output_type = output_config.type
        format_config = output_config.format
        _format = Formatter.from_config(format_config)
        log.debug("got format: %s", (_format))
        _output = Output.get_output_class(output_type, formatter=_format, output_config=output_config)
        log.debug("got output: %s", _output) 

        return _output
    
    def __init__(self, name=None) -> None:
        self.name = name

    @property
    def formatter(self):
        """ the formatter for this output """
        return getattr(self, "_formatter", None)

    @formatter.setter
    def formatter(self, formatter : AbstractFormat):
        self._formatter = formatter

    @abstractmethod
    def process(self, command=None, result: Result = None, device=None):
        """ entry point of any output class """
        raise NotImplementedError("need to implement process function")
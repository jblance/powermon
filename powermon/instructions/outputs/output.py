import logging
from enum import Enum

from rich import print

from .formatters import Formatter

# Set-up logger
log = logging.getLogger("outputs")


class OutputType(Enum):
    """ enum of valid output types """
    SCREEN = 'screen'
    MQTT = 'mqtt'
    API_MQTT = 'api_mqtt'


class Output():
    DEFAULT = OutputType.SCREEN

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
        elif output_type == OutputType.API_MQTT:
            from .api_mqtt import ApiMqtt
            output_class = ApiMqtt.from_config(output_config)
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
                    print(f"[GREEN]{name.upper()}[/]: {output}")
            except ModuleNotFoundError as exc:
                log.info("Error in module %s: %s", name, exc)
                continue
            except AttributeError as exc:
                log.info("Error in module %s: %s", name, exc)
                continue

    @staticmethod
    def multiple_from_config(outputs_config):
        """ return one or more output classes from a config """
        # outputs can be None,
        # str (eg screen),
        # list (eg [{'type': 'screen', 'format': 'simple'}, {'type': 'screen', 'format': {'type': 'htmltable'}}])
        # dict (eg {'format': 'table'})
        # print("outputs %s, type: %s" % (outputs, type(outputs)))
        _outputs = []
        log.debug("processing outputs_config: %s", outputs_config)
        if outputs_config is None:
            _outputs.append(Output.parse_output_config({"type": "screen", "format": Formatter.DEFAULT_FORMAT}))
        elif isinstance(outputs_config, str):
            # eg 'screen'
            _outputs.append(Output.parse_output_config({"type": outputs_config, "format": Formatter.DEFAULT_FORMAT}))
        elif isinstance(outputs_config, list):
            # eg [{'type': 'screen', 'format': 'simple'}, {'type': 'screen', 'format': {'type': 'htmltable'}}]
            for output_config in outputs_config:
                _outputs.append(Output.parse_output_config(output_config))
        elif isinstance(outputs_config, dict):
            # eg {'format': 'table'}
            _outputs.append(Output.parse_output_config(outputs_config))
        else:
            pass
        return _outputs

    @staticmethod
    def parse_output_config(output_config):
        """ generate a single output object from a config """
        log.debug("parse_output_config, config: %s", output_config)
        output_type = output_config.get("type", Output.DEFAULT)
        format_config = output_config.get("format", Formatter.DEFAULT_FORMAT)
        _format = Formatter.from_config(format_config)
        log.debug("got format: %s", (_format))
        _output = Output.get_output_class(output_type, formatter=_format, output_config=output_config)
        log.debug("got output: %s", _output)
        return _output
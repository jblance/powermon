""" outputs / __init__.py """
import logging
from enum import Enum, auto

# from strenum import LowercaseStrEnum

from powermon.outputformats import DEFAULT_FORMAT
from powermon.outputformats import from_config as format_from_config

# Set-up logger
log = logging.getLogger("outputs")

DEFAULT_OUTPUT = "screen"


class OutputType(Enum):
    """ enum of valid output types """
    SCREEN = auto()
    MQTT = auto()
    API_MQTT = auto()


def get_output_class(output_type, formatter, output_config=None):
    """ return the instantiated output class - inc formatter """
    output_class = None
    # Only import the required class
    log.debug("outputType %s", output_type)
    if output_type == OutputType.MQTT:
        from powermon.outputs.mqtt import MQTT
        output_class = MQTT.from_config(output_config)
        output_class.formatter = formatter
    elif output_type == OutputType.API_MQTT:
        from powermon.outputs.api_mqtt import ApiMqtt
        output_class = ApiMqtt.from_config(output_config)
        output_class.formatter = formatter
    else:
        from powermon.outputs.screen import Screen
        output_class = Screen.from_config(output_config)
        output_class.formatter = formatter
    return output_class


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
        _outputs.append(parse_output_config({"type": "screen", "format": DEFAULT_FORMAT}))
    elif isinstance(outputs_config, str):
        # eg 'screen'
        _outputs.append(parse_output_config({"type": outputs_config, "format": DEFAULT_FORMAT}))
    elif isinstance(outputs_config, list):
        # eg [{'type': 'screen', 'format': 'simple'}, {'type': 'screen', 'format': {'type': 'htmltable'}}]
        for output_config in outputs_config:
            _outputs.append(parse_output_config(output_config))
    elif isinstance(outputs_config, dict):
        # eg {'format': 'table'}
        _outputs.append(parse_output_config(outputs_config))
    else:
        pass
    return _outputs


def parse_output_config(output_config):
    """ generate a single output object from a config """
    log.debug("parse_output_config, config: %s", output_config)
    output_type = output_config.get("type", DEFAULT_OUTPUT)
    format_config = output_config.get("format", DEFAULT_FORMAT)
    _format = format_from_config(format_config)
    log.debug("got format: %s", (_format))
    _output = get_output_class(output_type, formatter=_format, output_config=output_config)
    log.debug("got output: %s", _output)
    return _output

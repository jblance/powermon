""" Package of the implemented protocols. 
Includes an Enumeration of available protocols, some helper functions 
as well as a Abstract Base Protocol and the protocol classes
"""
import importlib
import logging
from enum import StrEnum, auto

from rich.console import Console

from powermon.libs.errors import ConfigError
# from ..config.device_config import DeviceConfig


log = logging.getLogger("protocols")
rprint = Console(highlight=False).print

MAX_MODELS = ['MAX']
MST_MODELS = ['MST']

class Protocol(StrEnum):
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

    DEFAULT = PI30


def from_device_config(config: 'DeviceConfig') -> Protocol:
    """Get a protocol object from a DeviceConfig model

    Args:
        config (DeviceConfig): validated config model

    Returns:
        Protocol: instantiated protocol object matching the config
    """
    protocol_name = config.port.protocol
    model = config.model

    return from_name(name=protocol_name, model=model)


def from_name(name, model=None):
    """
    Get the protocol based on the protocol name and optionally device model
    """

    log.debug("Protocol: %s", name)

    protocol_id = name.lower()
    proto = None

    match protocol_id:
        case Protocol.DALY:
            from powermon.protocols.daly import Daly as proto
        case Protocol.NEEY | Protocol.HELTEC:
            from powermon.protocols.neey import Neey as proto
        case Protocol.PI18:
            from powermon.protocols.pi18 import PI18 as proto
        case Protocol.PI30:
            if model in MAX_MODELS:
                from powermon.protocols.pi30max import PI30MAX as proto
            elif model in MST_MODELS:
                from powermon.protocols.pi30mst import PI30MST as proto
            else:
                from powermon.protocols.pi30 import PI30 as proto
        case Protocol.PI30MAX:
            from powermon.protocols.pi30max import PI30MAX as proto
        case Protocol.PI30MST:
            from powermon.protocols.pi30mst import PI30MST as proto
        case Protocol.VED:
            from powermon.protocols.ved import VictronEnergyDirect as proto
        case Protocol.JKSERIAL:
            from powermon.protocols.jkserial import JkSerial as proto
        case _:
            raise ConfigError(f"Invalid protocol_id, no protocol found for: '{protocol_id}'")
    return proto()


def list_protocols():
    """ helper function to display the list of supported protocols """
    rprint("[bold yellow]Supported protocols")
    for name in Protocol:
        try:
            _proto = from_name(name)
            if _proto is not None:
                rprint(f"[green]{name.upper()}[/]: {_proto}")
        except ModuleNotFoundError as exc:
            log.info("Error in module %s: %s", name, exc)
            continue
        except AttributeError as exc:
            log.info("Error in module %s: %s", name, exc)
            continue


def list_commands(name: str=None):
    """ helper function to display the commands available for a specified protocol

    Args:
        name (str, optional): Name of protocol to list commands from. Defaults to None.
    """
    try:
        _proto = from_name(name)
        command_definitions = _proto.list_commands()
        # print(command_definitions)
        rprint(f"Commands in protocol: [bold yellow]{name.upper()}")
        for item in command_definitions:
            rprint(f"[green]{item}[/] [cyan]{command_definitions[item].aliases}[/cyan] - {command_definitions[item].description} {command_definitions[item].help_text}")
    except ConfigError:
        rprint(f"[bold red]Protocol {name} not found")
    return

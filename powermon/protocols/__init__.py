""" Package of the implemented protocols. 
Includes an Enumeration of available protocols, some helper functions 
as well as a Abstract Base Protocol and the protocol classes
"""
import importlib
import logging
from enum import StrEnum, auto

from rich.console import Console

from powermon.libs.errors import ConfigError


log = logging.getLogger("protocols")
rprint = Console(highlight=False).print


class Protocol(StrEnum):
    """Enumeration of currently implemented Protocols"""
    PI18 = auto()  # WIP
    PI30 = auto()
    PI30MAX = auto()
    # PI30MAXA = auto()
    PI30MST = auto()
    DALY = auto()
    NEEY = auto()
    HELTEC = auto()
    VED = auto()
    JKSERIAL = auto()


def get_protocol_definition(protocol, model=None):
    """
    Get the protocol based on the protocol name and optionally device model
    """

    log.debug("Protocol: %s", protocol)

    protocol_id = protocol.lower()

    match protocol_id:
        case Protocol.DALY:
            from powermon.protocols.daly import Daly
            return Daly()
        case Protocol.NEEY | Protocol.HELTEC:
            from powermon.protocols.neey import Neey
            return Neey()
        case Protocol.PI18:
            from powermon.protocols.pi18 import PI18
            return PI18()
        case Protocol.PI30:
            from powermon.protocols.pi30 import PI30
            return PI30(model=model)
        case Protocol.PI30MAX:
            from powermon.protocols.pi30 import PI30
            return PI30(model="MAX")
        case Protocol.PI30MST:
            from powermon.protocols.pi30 import PI30
            return PI30(model='MST')
        case Protocol.VED:
            from powermon.protocols.ved import VictronEnergyDirect
            return VictronEnergyDirect()
        case Protocol.JKSERIAL:
            from powermon.protocols.jkserial import JkSerial
            return JkSerial()
        case _:
            raise ConfigError(f"Invalid protocol_id, no protocol found for: '{protocol_id}'")
    return None


def list_protocols():
    """ helper function to display the list of supported protocols """
    rprint("[bold yellow]Supported protocols")
    for name in Protocol:
        try:
            _proto = get_protocol_definition(name)
            if _proto is not None:
                rprint(f"[green]{name.upper()}[/]: {_proto}")
        except ModuleNotFoundError as exc:
            log.info("Error in module %s: %s", name, exc)
            continue
        except AttributeError as exc:
            log.info("Error in module %s: %s", name, exc)
            continue


def list_commands(protocol: str=None):
    """ helper function to display the commands available for a specified protocol

    Args:
        protocol (str, optional): Name of protocol to list commands from. Defaults to None.
    """
    try:
        _proto = get_protocol_definition(protocol)
        command_definitions = _proto.list_commands()
        # print(command_definitions)
        rprint(f"Commands in protocol: [bold yellow]{protocol.upper()}")
        for item in command_definitions:
            rprint(f"[green]{item}[/] [cyan]{command_definitions[item].aliases}[/cyan] - {command_definitions[item].description} {command_definitions[item].help_text}")
    except ConfigError:
        rprint(f"[bold red]Protocol {protocol} not found")
    return

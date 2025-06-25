""" Package of the implemented protocols. 
Includes an Enumeration of available protocols, some helper functions 
as well as a Abstract Base Protocol and the protocol classes
"""
import logging

from rich.console import Console

from .protocol_types import ProtocolType
from ....powermon_exceptions import ConfigError


log = logging.getLogger("protocols")
rprint = Console(highlight=False).print



class Protocol():
    DEFAULT = ProtocolType.PI30
    MAX_MODELS = ['MAX']
    MST_MODELS = ['MST']

    @staticmethod
    def from_device_config(config) -> 'Protocol':
        """Get a protocol object from a DeviceConfig model

        Args:
            config (DeviceConfig): validated config model

        Returns:
            Protocol: instantiated protocol object matching the config
        """
        protocol_name: str = config.port.protocol
        model: str = config.model

        return Protocol.from_name(name=protocol_name, model=model)

    @staticmethod
    def from_name(name, model=None):
        """
        Get the protocol based on the protocol name and optionally device model
        """

        log.debug("Protocol: %s", name)

        protocol_id: str = name.lower()
        # proto = None

        match protocol_id:
            case ProtocolType.DALY:
                from .daly import Daly as proto
            case ProtocolType.NEEY | ProtocolType.HELTEC:
                from .neey import Neey as proto
            case ProtocolType.PI18:
                from .pi18 import PI18 as proto
            case ProtocolType.PI30:
                if model in Protocol.MAX_MODELS:
                    from .pi30max import PI30MAX as proto
                elif model in Protocol.MST_MODELS:
                    from .pi30mst import PI30MST as proto
                else:
                    from .pi30 import PI30 as proto
            case ProtocolType.PI30MAX:
                from .pi30max import PI30MAX as proto
            case ProtocolType.PI30MST:
                from .pi30mst import PI30MST as proto
            case ProtocolType.VED:
                from .ved import VictronEnergyDirect as proto
            case ProtocolType.JKSERIAL:
                from .jkserial import JkSerial as proto
            case _:
                raise ConfigError(f"Invalid protocol_id, no protocol found for: '{protocol_id}'")
        return proto()


def list_protocols():
    """ helper function to display the list of supported protocols """
    rprint("[bold yellow]Supported protocols")
    for name in ProtocolType:
        try:
            _proto = Protocol.from_name(name)
            if _proto is not None:
                rprint(f"[green]{name.upper()}[/]: {_proto}")
        except ModuleNotFoundError as exc:
            log.info("Error in module %s: %s", name, exc)
            continue
        except AttributeError as exc:
            log.info("Error in module %s: %s", name, exc)
            continue


def list_commands(name: str):
    """ helper function to display the commands available for a specified protocol

    Args:
        name (str, optional): Name of protocol to list commands from. Defaults to None.
    """
    try:
        _proto = Protocol.from_name(name)
        command_definitions = _proto.list_commands()
        # print(command_definitions)
        rprint(f"Commands in protocol: [bold yellow]{name.upper()}")
        for item in command_definitions:
            rprint(f"[green]{item}[/] [cyan]{command_definitions[item].aliases}[/cyan] - {command_definitions[item].description} {command_definitions[item].help_text}")
    except ConfigError:
        rprint(f"[bold red]Protocol {name} not found")
    return

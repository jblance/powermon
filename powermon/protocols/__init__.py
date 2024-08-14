""" protocol __init__.py """
import importlib
import logging
from enum import StrEnum, auto

# from strenum import LowercaseStrEnum

from powermon.libs.errors import ConfigError

log = logging.getLogger("protocols")


class Protocol(StrEnum):
    """ enumerate available protocols """
    PI18 = auto()  # WIP
    PI30 = auto()
    PI30MAX = auto()
    DALY = auto()
    NEEY = auto()
    VED = auto()
    JKSERIAL = auto()


def get_protocol_definition(protocol):
    """
    Get the protocol based on the protocol name
    """

    log.debug("Protocol: %s", protocol)

    protocol_id = protocol.lower()

    match protocol_id:
        case Protocol.DALY:
            from powermon.protocols.daly import Daly
            return Daly()
        case Protocol.NEEY:
            from powermon.protocols.neey import Neey
            return Neey()
        case Protocol.PI18:
            from powermon.protocols.pi18 import PI18
            return PI18()
        case Protocol.PI30:
            from powermon.protocols.pi30 import PI30
            return PI30()
        case Protocol.PI30MAX:
            from powermon.protocols.pi30max import PI30MAX
            return PI30MAX()
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
    """ helper function to display a list of supported protocols """
    print("Supported protocols")
    for name in Protocol:
        try:
            _proto = get_protocol_definition(name)
            if _proto is not None:
                print(f"{name}: {_proto}")
        except ModuleNotFoundError as exc:
            log.info("Error in module %s: %s", name, exc)
            continue
        except AttributeError as exc:
            log.info("Error in module %s: %s", name, exc)
            continue
        # print(f"{name}: {_module()}")

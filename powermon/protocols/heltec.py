""" protocols / heltec.py """
import logging

from powermon.protocols.neey import Neey

log = logging.getLogger("heltec")


class Heltec(Neey):
    """
    Heltec Active Balancer protocol handler
    """

    def __str__(self):
        return "Heltec Active Balancer protocol handler"

    def __init__(self) -> None:
        super().__init__()
        self.protocol_id = b"Heltec"
        self.check_definitions_count(expected=None)

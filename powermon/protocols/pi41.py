import logging

from .pi30 import pi30

log = logging.getLogger('powermon')


class pi41(pi30):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self._protocol_id = b'PI41'
        # self.COMMANDS = COMMANDS
        # log.info(f'Using protocol {self._protocol_id} with {len(self.COMMANDS)} commands')

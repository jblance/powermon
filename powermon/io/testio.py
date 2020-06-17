# shamelessly stolen from ccrisan https://github.com/qtoggle/qtoggleserver-mppsolar/blob/master/qtoggleserver/mppsolar/io.py
import logging

from .baseio import BaseIO

log = logging.getLogger('powermon')


class TestIO(BaseIO):
    def __init__(self) -> None:
        self._test_data = b'1234567890'
        self._counter = 0

    def read_available(self) -> bytes:
        result = self._test_data[self._counter]
        self._counter += 1
        if self._counter > len(self._test_data):
            self._counter = 0
        return result

    def write(self, data: bytes) -> None:
        self._test_data = data
        self._counter = 0

    def close(self) -> None:
        pass

    @staticmethod
    def supports(serial_device):
        if not serial_device:
            return False
        if serial_device.lower() == 'test':
            return True
        return False

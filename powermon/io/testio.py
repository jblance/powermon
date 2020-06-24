# shamelessly stolen from ccrisan https://github.com/qtoggle/qtoggleserver-mppsolar/blob/master/qtoggleserver/mppsolar/io.py
import logging

from .baseio import BaseIO

log = logging.getLogger('powermon')


class TestIO(BaseIO):
    def __init__(self) -> None:
        self._test_data = "(230.0 50.0 0030 42.0 54.0 56.4 46.0 60 0 0 2 0 0 0 0 0 1 1 0 0 1 0 54.0 0 1 000\x9E\x60\r"
        self._counter = 0

    def read_available(self) -> bytes:
        result = self._test_data[self._counter]
        self._counter += 1
        if self._counter > len(self._test_data):
            self._counter = 0
        return bytes(result, 'utf-8')

    def write(self, data: bytes) -> None:
        # self._test_data = data
        self._counter = 0

    def close(self) -> None:
        pass

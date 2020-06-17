# shamelessly stolen from ccrisan https://github.com/qtoggle/qtoggleserver-mppsolar/blob/master/qtoggleserver/mppsolar/io.py
import logging
import os
import re

from .baseio import BaseIO

log = logging.getLogger('powermon')


class HIDRawIO(BaseIO):
    def __init__(self, device_path: str) -> None:
        self._fd = os.open(device_path, flags=os.O_RDWR | os.O_NONBLOCK)

    def read_available(self) -> bytes:
        return os.read(self._fd, 1024)

    def write(self, data: bytes) -> None:
        os.write(self._fd, data)

    def close(self) -> None:
        os.close(self._fd)

    @staticmethod
    def supports(serial_device):
        if not serial_device:
            return False
        match = re.search("^.*hidraw\\d$", serial_device)
        if match:
            log.debug("Device matches hidraw regex")
            return True
        match = re.search("^.*mppsolar\\d$", serial_device)
        if match:
            log.debug("Device matches mppsolar regex")
            return True
        return False

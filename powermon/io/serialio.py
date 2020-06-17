# shamelessly stolen from ccrisan https://github.com/qtoggle/qtoggleserver-mppsolar/blob/master/qtoggleserver/mppsolar/io.py
import serial

from .baseio import BaseIO


class SerialIO(BaseIO):
    def __init__(self, serial_port, serial_baud=2400) -> None:
        self._serial: serial.Serial = serial.Serial(serial_port, serial_baud)

    def read_available(self) -> bytes:
        in_waiting = self._serial.in_waiting
        if in_waiting:
            return self._serial.read(in_waiting)

        return b''

    def write(self, data: bytes) -> None:
        self._serial.write(data)

    def close(self) -> None:
        self._serial.close()

    @staticmethod
    def supports(serial_device):
        return True

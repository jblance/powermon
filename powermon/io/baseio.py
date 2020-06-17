# shamelessly stolen from ccrisan https://github.com/qtoggle/qtoggleserver-mppsolar/blob/master/qtoggleserver/mppsolar/io.py
import abc
from time import sleep


class BaseIO(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def read_available(self) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def write(self, data: bytes) -> None:
        raise NotImplementedError

    def read(self, timeout: int) -> bytes:
        data = b''
        for _ in range(timeout * 10):
            data += self.read_available()
            if data.endswith(b'\r'):
                break

            sleep(0.1)

        return data

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def supports(communications) -> bool:
        raise NotImplementedError

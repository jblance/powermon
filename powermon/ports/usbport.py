""" powermon / ports / usbport.py """
# import asyncio
import logging
import os
import time
from glob import glob

from powermon.commands.command import Command
from powermon.commands.result import Result, ResultType
from powermon.libs.errors import ConfigError, PowermonProtocolError
from powermon.ports import PortType
from powermon.ports.abstractport import AbstractPort, _AbstractPortDTO
from powermon.protocols import get_protocol_definition

log = logging.getLogger("USBPort")


class UsbPortDTO(_AbstractPortDTO):
    """ data transfer model for SerialPort class """
    path: str
    serial_number: None | int | str


class USBPort(AbstractPort):
    """ usb port object """
    @classmethod
    async def from_config(cls, config=None):
        log.debug("building usb port. config:%s", config)
        path = config.get("path", "/dev/hidraw0")
        serial_number = config.get("serial_number")
        # get protocol handler, default to PI30 if not supplied
        protocol = get_protocol_definition(protocol=config.get("protocol", "PI30"))
        # instantiate class
        _class = cls(path=path, protocol=protocol)
        # deal with wildcard path resolution
        _class.path = await _class.resolve_path(path, serial_number)
        return _class

    def __init__(self, path, protocol) -> None:
        self.port_type = PortType.USB
        super().__init__(protocol=protocol)

        self.path = None
        self.port = None


    async def resolve_path(self, path, serial_number):
        """Async method to resolve a valid path by testing each one."""
        # expand 'wildcard'
        paths = glob(path)
        if not paths:
            raise ConfigError(f"No matching paths found on this system for {path}")

        if len(paths) == 1:
            return paths[0]  # only one valid result

        # More than one valid path
        # check we have something to look for
        if serial_number is None:
            raise ConfigError("Wildcard paths require a serial_number in config.")
        # check we have get_id in this protocol
        try:
            command = self.protocol.get_id_command()
        except PowermonProtocolError as ex:
            raise ConfigError(f"No get_id in protocol: {self.protocol.protocol_id}") from ex

        for _path in paths:
            log.debug("Checking path: %s for serial_number: %s", _path, serial_number)
            self.path = _path
            await self.connect()
            res = await self.send_and_receive(command=command)
            await self.disconnect()

            if res.is_valid and str(res.readings[0].data_value) == str(serial_number):
                log.info("SUCCESS: path: %s matches serial_number: %s", _path, serial_number)
                return _path  # return the matching path
        raise ConfigError(f"None of the paths match serial_number: {serial_number}")


    def to_dto(self):
        dto = UsbPortDTO(port_type="usb", path=self.path, protocol=self.protocol.to_dto())
        return dto

    def is_connected(self) -> bool:
        return self.port is not None

    async def connect(self) -> bool:
        if self.is_connected():
            log.debug("USBPort already connected")
            return True
        log.debug("USBPort connecting. path:%s, protocol:%s", self.path, self.protocol)
        try:
            self.port = os.open(self.path, os.O_RDWR | os.O_NONBLOCK)
            log.debug("USBPort port number $%s", self.port)
        except Exception as e:
            log.warning("Error openning usb port: %s", e)
            self.port = None
            self.error_message = e
        return self.is_connected()

    async def disconnect(self) -> None:
        log.debug("USBPort disconnecting: %i", self.port)
        if self.port is not None:
            os.close(self.port)
        self.port = None

    async def send_and_receive(self, command: Command) -> Result:
        if not self.is_connected():
            log.warning("USBPort not connected")
            return command.build_result(result_type=ResultType.ERROR, raw_response=b"USBPort not connected", protocol=self.protocol)
        response_line = bytes()

        # Send the command to the open usb connection
        full_command = command.full_command
        cmd_len = len(full_command)
        log.debug("length of to_send: %i", cmd_len)
        # for command of len < 8 it ok just to send
        # otherwise need to pack to a multiple of 8 bytes and send 8 at a time
        try:
            if cmd_len <= 8:
                # Send all at once
                log.debug("sending full_command in on shot")
                time.sleep(0.05)
                os.write(self.port, full_command)
            else:
                log.debug("multiple chunk send")
                chunks = [full_command[i:i + 8] for i in range(0, cmd_len, 8)]
                for chunk in chunks:
                    # pad chunk to 8 bytes
                    if len(chunk) < 8:
                        padding = 8 - len(chunk)
                        chunk += b'\x00' * padding
                    log.debug("sending chunk: %s", chunk)
                    time.sleep(0.05)
                    os.write(self.port, chunk)
            time.sleep(0.25)
            # Read from the usb connection
            # try to a max of 100 times
            for _ in range(100):
                # attempt to deal with resource busy and other failures to read
                time.sleep(0.15)
                r = os.read(self.port, 256)
                response_line += r
                # Finished is \r is in byte_response
                if bytes([13]) in response_line:
                    # remove anything after the \r
                    response_line = response_line[: response_line.find(bytes([13])) + 1]
                    break
        except BrokenPipeError as e:
            log.debug("USB read error: %s", e)
        log.debug("usb response was: %s", response_line)
        # response = self.get_protocol().check_response_and_trim(response_line)
        result = command.build_result(raw_response=response_line, protocol=self.protocol)

        return result

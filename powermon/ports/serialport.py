""" powermon / ports / serialport.py """
import asyncio
import logging
import time
from glob import glob

import serial
from tenacity import retry, stop_after_attempt, wait_fixed  # https://tenacity.readthedocs.io/en/latest/

from powermon.commands.command import Command, CommandType
from powermon.commands.result import Result
from powermon.libs.errors import ConfigError, InvalidResponse, PowermonProtocolError
from powermon.ports import PortType
from powermon.ports.abstractport import AbstractPort, _AbstractPortDTO
from powermon.protocols import get_protocol_definition

log = logging.getLogger("SerialPort")

VICTRON_LINES_TO_READ = 30
READ_UNTIL_DONE_WAIT_TIME = 0.5


class SerialPortDTO(_AbstractPortDTO):
    """ data transfer model for SerialPort class """
    path: str
    baud: int
    serial_number: None | int | str

class SerialPort(AbstractPort):
    """ serial port object - normally a usb to serial adapter """

    def __str__(self):
        return f"SerialPort: {self.path=}, {self.baud=}, protocol:{self.protocol}, {self.serial_port=}, {self.error_message=}"

    @classmethod
    async def from_config(cls, config=None):
        log.debug("building serial port. config:%s", config)
        path = config.get("path", "/dev/ttyUSB0")
        baud = config.get("baud", 2400)
        serial_number = config.get("serial_number")
        # get protocol handler, default to PI30 if not supplied
        protocol = get_protocol_definition(protocol=config.get("protocol", "PI30"))
        # instantiate class
        _class = cls(path=path, baud=baud, protocol=protocol)
        # deal with wildcard path resolution
        _class.path = await _class.resolve_path(path, serial_number)


    def __init__(self, path, baud, protocol) -> None:
        self.port_type = PortType.SERIAL
        super().__init__(protocol=protocol)

        self.path = path
        self.baud = baud
        self.serial_port = None


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
        # Get the protocol's ID command
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

            if res.is_valid and res.readings[0].data_value == serial_number:
                log.info("SUCCESS: path: %s matches serial_number: %s", _path, serial_number)
                return _path  # return the matching path
        raise ConfigError(f"None of the paths match serial_number: {serial_number}")


    def to_dto(self) -> _AbstractPortDTO:
        dto = SerialPortDTO(port_type="serial", path=self.path, baud=self.baud, protocol=self.protocol.to_dto())
        return dto


    def is_connected(self):
        return self.serial_port is not None and self.serial_port.is_open


    async def connect(self) -> int:
        log.debug("SerialPort port connecting. path:%s, baud:%s", self.path, self.baud)
        try:
            self.serial_port = serial.Serial(port=self.path, baudrate=self.baud, timeout=1, write_timeout=1)
            log.debug(self.serial_port)
        except ValueError as e:
            log.error("Incorrect configuration for serial port: %s", e)
            self.error_message = str(e)
            self.serial_port = None
        except serial.SerialException as e:
            log.error("Error opening serial port: %s", e)
            self.error_message = str(e)
            self.serial_port = None
        return self.is_connected()


    async def disconnect(self) -> None:
        log.debug("SerialPort disconnecting")
        if self.serial_port is not None:
            self.serial_port.close()
        self.serial_port = None


    async def send_and_receive(self, command: Command) -> Result:
        full_command = command.full_command
        response_line = None
        log.info("port: %s, full_command: %s", self.serial_port, full_command)
        if not self.is_connected():
            raise RuntimeError("Serial port not open")
        try:
            log.debug("Executing command via SerialPort...")
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            # Process i/o differently depending on command type
            command_defn = command.command_definition
            match command_defn.command_type:
                case CommandType.VICTRON_LISTEN:
                    # this command type doesnt need to send a command, it just listens on the serial port
                    log.debug("case: CommandType.VICTRON_LISTEN, listening for %i lines", VICTRON_LINES_TO_READ)
                    response_line = b""
                    for _ in range(VICTRON_LINES_TO_READ):
                        _response = self.serial_port.read_until(b"\n")
                        response_line += _response
                case CommandType.SERIAL_READONLY:
                    # read until no more data
                    log.debug("CommandType.SERIAL_READONLY")
                    response_line = b""
                    while True:
                        await asyncio.sleep(0.2)  # give serial port time to receive the data
                        to_read = self.serial_port.in_waiting
                        log.debug("bytes waiting: %s", to_read)
                        if to_read == 0:
                            break
                        # got some data to read
                        response_line += self.serial_port.read(to_read)
                case CommandType.SERIAL_READ_UNTIL_DONE:
                    # this case reads until no more to read or timeout
                    response_line = await self._serial_read_until_done(full_command)
                case _:
                    # default processing
                    self.serial_port.reset_input_buffer()
                    self.serial_port.reset_output_buffer()
                    c = self.serial_port.write(full_command)
                    log.debug("Default serial s&r. Wrote %i bytes", c)
                    self.serial_port.flush()
                    time.sleep(0.3)  # give serial port time to receive the data
                    response_line = self.serial_port.read_until(b"\r")
            log.info("serial response was: %s", response_line)
            # response = self.get_protocol().check_response_and_trim(response_line)
            result = command.build_result(raw_response=response_line, protocol=self.protocol)
            return result
        except Exception as e:
            log.warning("Serial read error: %s", e)
            result.error = True
            result.error_messages.append(f"Serial read error {e}")
            self.disconnect()
            return result


    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    async def _serial_read_until_done(self, full_command):
        log.debug("case: CommandType.SERIAL_READ_UNTIL_DONE")
        response_line = b""
        self.serial_port.timeout = 0.5
        self.serial_port.write_timeout = 1
        self.serial_port.reset_input_buffer()
        self.serial_port.reset_output_buffer()
        c = self.serial_port.write(full_command)
        log.debug("wrote %s bytes", c)
        self.serial_port.flush()
        # read until no more data
        time.sleep(READ_UNTIL_DONE_WAIT_TIME)
        to_read = self.serial_port.in_waiting
        log.debug("initial bytes waiting %s", to_read)
        while to_read > 0:
            # await asyncio.sleep(0.5)  # give serial port time to receive the data
            # got some data to read
            log.debug("bytes waiting %s", to_read)
            response_line += self.serial_port.read(to_read)
            time.sleep(READ_UNTIL_DONE_WAIT_TIME)
            to_read = self.serial_port.in_waiting
        if len(response_line) == 0:
            # maybe port has failed
            await self.disconnect()
            await self.connect()
            log.info("response was empty")
            raise InvalidResponse("Response was empty")
        return response_line
        
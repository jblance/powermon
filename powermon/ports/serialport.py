""" powermon / ports / serialport.py """
import asyncio
import logging
import time
from glob import glob

import serial
from tenacity import retry, stop_after_attempt, wait_fixed

from powermon.commands.command import Command, CommandType
from powermon.commands.result import Result
from powermon.libs.errors import ConfigError, InvalidResponse
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
    def from_config(cls, config=None):
        log.debug("building serial port. config:%s", config)
        path = config.get("path", "/dev/ttyUSB0")
        baud = config.get("baud", 2400)
        serial_number = config.get("serial_number")
        # get protocol handler, default to PI30 if not supplied
        protocol = get_protocol_definition(protocol=config.get("protocol", "PI30"))
        return cls(path=path, baud=baud, protocol=protocol, serial_number=serial_number)

    def __init__(self, path, baud, protocol, serial_number) -> None:
        self.port_type = PortType.SERIAL
        super().__init__(protocol=protocol)

        self.path = None
        self.baud = baud
        self.serial_port = None
        # self.serial_number = serial_number
        # using glob to determine path(s)
        paths = glob(path)
        path_count = len(paths)
        match path_count:
            case 0:
                log.error("no matching paths found on this system for: %s", path)
                raise ConfigError(f"no matching paths found on this system for {path}")
            case 1:
                # only one valid result on this system
                self.path = paths[0]
            case _:
                # more than one valid path - so we need to determine which to use
                if serial_number is None:
                    raise ConfigError("To use wildcard paths an serial_number must be specified in the config file for the port")
                # need to build a command
                command = self.protocol.get_id_command()
                for _path in paths:
                    log.debug("Multiple paths - checking path: %s to see if it matches %s", _path, serial_number)
                    self.path = _path
                    asyncio.run(self.connect())
                    res = asyncio.run(self.send_and_receive(command=command))
                    asyncio.run(self.disconnect())
                    if not res.is_valid:
                        log.debug("path: %s does not match for serial_number: %s", _path, serial_number)
                        # asyncio.run(self.disconnect())
                        continue
                    if res.readings[0].data_value == serial_number:
                        log.info("SUCCESS: path: %s matches for serial_number: %s", _path, serial_number)
                        return
                raise ConfigError(f"Multiple paths - none of {paths} match {serial_number}")
        # end of multi-path logic

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
        
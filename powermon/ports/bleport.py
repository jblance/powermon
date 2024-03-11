""" powermon / ports / bleport.py """
# import serial
import asyncio
import logging

try:
    from bleak import BleakClient
except ImportError:
    print("You are missing a python library - 'bleak'")
    print("To install it, use the below command:")
    print("    python -m pip install 'powermon[ble]'")
    print("or:")
    print("    python -m pip install bleak")
    return


from powermon.commands.command import Command, CommandType
from powermon.commands.result import Result
from powermon.dto.portDTO import PortDTO
from powermon.libs.errors import PowermonWIP
from powermon.ports.abstractport import AbstractPort
from powermon.ports.porttype import PortType
from powermon.protocols import get_protocol_definition

log = logging.getLogger("BlePort")


class BlePort(AbstractPort):
    """ BLE port object """

    def __str__(self):
        return f"BlePort: {self.mac=}, protocol:{self.protocol}, {self.client=}, {self.error_message=}"

    @classmethod
    def from_config(cls, config=None):
        log.debug("building ble port. config:%s", config)
        mac = config.get("mac")
        # get protocol handler, default to PI30 if not supplied
        protocol = get_protocol_definition(protocol=config.get("protocol", "PI30"))
        return cls(mac=mac, protocol=protocol)

    def __init__(self, mac, protocol) -> None:
        super().__init__(protocol=protocol)
        self.port_type = PortType.SERIAL
        self.mac = mac
        self.client = None
        self.is_protocol_supported()
        # self.error_message = None
        self.response_cache = {}

    def to_dto(self) -> PortDTO:
        dto = PortDTO(type="ble", mac=self.mac, protocol=self.protocol.to_dto())
        return dto

    def _notification_callback(self, handle, data):
        log.debug("%s %s %s", handle, repr(data), len(data))
        print(f"callback - {handle=}, {data=}")
        return
        # responses = []
        # command_code =90
        # if len(data) == 13:
        #     responses.append(data)
        # elif len(data) == 26:
        #     responses.append(data[0:13])
        #     responses.append(data[13:])
        # else:
        #     # self.logger.error(len(data), "bytes received, not 13 or 26, not implemented")
        #     pass

        # for response_bytes in responses:
        #     #command = response_bytes[2:3].hex()
        #     if self.response_cache["done"] is True:
        #         # self.logger.debug("skipping response for %s, done" % command)
        #         return
        #     self.response_cache["queue"].append(response_bytes[4:-1])
        #     if len(self.response_cache["queue"]) == self.response_cache["max_responses"]:
        #         self.response_cache["done"] = True
        #         self.response_cache["future"].set_result(self.response_cache["queue"])

    def disconnect_callback(self, client):
        """ callback for disconnection """
        print(f"disconnect callback, {client=}")
        self.client = None

    def is_connected(self):
        return self.client is not None and self.client.is_connected

    async def connect(self) -> int:
        log.debug("bleport connecting. mac:%s", self.mac)
        try:
            # build client object
            self.client = BleakClient(self.mac, disconnected_callback=self.disconnect_callback)
            # connect to client
            await self.client.connect()
            # 'turn on' notification characteristic
            # await self.client.start_notify(17, self._notification_callback)
            # write to 'XXX' charateristic
            # await self.client.write_gatt_char(48, bytearray(b""))
            log.debug(self.client)
        except Exception as e:
            # log.error("Incorrect configuration for serial port: %s", e)
            # self.error_message = str(e)
            print(e)
            self.client = None
            raise PowermonWIP("connect failed") from e
        
        return self.is_connected()

    async def disconnect(self) -> None:
        log.debug("usbserial port disconnecting")
        if self.client is not None:
            await self.client.disconnect()
        self.client = None

    async def send_and_receive(self, command: Command) -> Result:
        full_command = command.full_command
        command_code = 90
        self.response_cache = {"queue": [],
                                "future": asyncio.Future(),
                                "max_responses": 3,
                                "done": False}
        response_line = None
        log.debug("port: %s, full_command: %s", self.client, full_command)
        if not self.is_connected():
            raise RuntimeError("Ble port not open")
        # try:
        log.debug("Executing command via ble...")
        await self.client.write_gatt_char(15, full_command)
        log.debug("Waiting...")
        try:
            response_line = await asyncio.wait_for(self.response_cache["future"], 30)
        except asyncio.TimeoutError:
            log.warning("Timeout while waiting for %s response" % command)
            exit(1)
            return False
        print("got %s" % response_line)
        #return result
        # self.serial_port.reset_input_buffer()
        # self.serial_port.reset_output_buffer()
        # # Process i/o differently depending on command type
        # command_defn = command.command_definition
        # match command_defn.command_type:
        #     case CommandType.VICTRON_LISTEN:
        #         # this command type doesnt need to send a command, it just listens on the serial port
        #         _lines = 30
        #         log.debug("VictronCommandType.LISTEN s&r, listening for %i lines", _lines)
        log.debug("serial response was: %s", response_line)
        # response = self.get_protocol().check_response_and_trim(response_line)
        result = command.build_result(raw_response=response_line, protocol=self.protocol)
        return result
        # except Exception as e:
        #     log.warning("Serial read error: %s", e)
        #     result.error = True
        #     result.error_messages.append(f"Serial read error {e}")
        #     self.disconnect()
        #     return result

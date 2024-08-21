""" bleport module ....
"""
# import serial
import asyncio
import logging
import subprocess

try:
    from bleak import BleakClient, BleakScanner
    from bleak.exc import BleakDeviceNotFoundError
except ImportError:
    print("You are missing a python library - 'bleak'")
    print("To install it, use the below command:")
    print("    python -m pip install 'powermon[ble]'")
    print("or:")
    print("    python -m pip install bleak")
    exit(1)


from powermon.commands.command import Command
from powermon.commands.result import Result
from powermon.libs.errors import (BLEResponseError, ConfigError,
                                  PowermonProtocolError, PowermonWIP)
from powermon.ports import PortType
from powermon.ports.abstractport import AbstractPort, AbstractPortDTO
from powermon.protocols import get_protocol_definition

log = logging.getLogger("BlePort")


class BlePort(AbstractPort):
    """ represents a BLE port - extends AbstractPort

    Args:
        AbstractPort (_type_): _description_
    """

    def __str__(self):
        return f"BlePort: {self.mac=}, protocol:{self.protocol}, {self.client=}, {self.error_message=}"

    @classmethod
    def from_config(cls, config: dict|None = None):
        log.debug("building ble port. config:%s", config)
        if config is None:
            raise ConfigError("BLE port config missing")
        mac = config.get("mac")
        # get handles
        # notifier_handle = config.get("notifier_handle", 17)
        # intializing_handle = config.get("intializing_handle", 48)
        # command_handle = config.get("command_handle", 15)
        # get protocol handler, default to PI30 if not supplied
        protocol = get_protocol_definition(protocol=config.get("protocol", "PI30"))
        return cls(mac=mac, protocol=protocol)

    def __init__(self, mac, protocol) -> None:
        super().__init__(protocol=protocol)
        self.port_type = PortType.BLE
        self.protocol.port_type = self.port_type
        self.is_protocol_supported()
        self.mac = mac
        # set handles (from protocol? override from config??)
        self.notifier_handle: int = getattr(self.protocol, "notifier_handle", 0)
        self.intializing_handle: int = getattr(self.protocol, "intializing_handle", 0)
        self.command_handle: int = getattr(self.protocol, "command_handle", 0)
        # Check that the needed handles are defined
        if not self.notifier_handle:
            raise PowermonProtocolError("notifier_handle needs to be defined in protocol: {self.protocol.protocol_id}")
        if not self.command_handle:
            raise PowermonProtocolError("command_handle needs to be defined in protocol: {self.protocol.protocol_id}")
        self.response = bytearray()
        self.client: BleakClient|None = None

    def to_dto(self) -> AbstractPortDTO:
        dto = AbstractPortDTO(port_type="ble", protocol=self.protocol.to_dto())  # TODO: add correct dto
        return dto

    def _notification_callback(self, handle, data):
        log.debug("%s %s %s", handle, repr(data), len(data))
        self.response += data
        return

    def is_connected(self) -> bool:
        """ is this port connected to a device 

        Returns:
            bool: True if port is defined and connected
        """
        return self.client is not None and self.client.is_connected

    async def connect(self) -> bool:
        """ try to find and connect to the device identified by self.mac

        Raises:
            BleakDeviceNotFoundError: could not find or connect to the identified device
            PowermonWIP: unexpected error - signified code updates are needed

        Returns:
            bool: True is connection successful
        """
        log.info("bleport connecting. mac:%s", self.mac)
        try:
            # find ble client
            bledevice = await BleakScanner.find_device_by_address(device_identifier=self.mac, timeout=10.0)
            if bledevice is None:
                raise BleakDeviceNotFoundError(f"Device with address: {self.mac} was not found.")
            log.info("got bledevice: %s", bledevice)
            # build client object
            self.client = BleakClient(bledevice)
            log.info("got bleclient: %s", self.client)
            # connect to client
            await self.client.connect()
            log.info("bleclient connected")
            # 'turn on' notification characteristic
            await self.client.start_notify(self.notifier_handle, self._notification_callback)
            # flush initializing characteristic?
            if self.intializing_handle:
                await self.client.write_gatt_char(self.intializing_handle, bytearray(b""))
            log.debug(self.client)
        except BleakDeviceNotFoundError as e:
            print(f'not found error {e!r}')
        except Exception as e:
            # log.error("Incorrect configuration for serial port: %s", e)
            # self.error_message = str(e)
            print(e)
            self.client = None
            raise PowermonWIP("connect failed") from e
        return self.is_connected()

    async def disconnect(self) -> None:
        log.info("ble port disconnecting, %s %s", self.client, self.is_connected())
        if self.client is not None and self.client.is_connected:
            # for some reason client.disconnect doesnt seem to work - just hangs...
            # await self.client.disconnect()
            open_blue = subprocess.Popen(["bluetoothctl"], shell=True, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
            open_blue.communicate(b"disconnect %s\n" % self.mac.encode('utf-8'))
            open_blue.kill()
        self.client = None

    async def send_and_receive(self, command: Command) -> Result:
        full_command = command.full_command
        log.debug("port: %s, full_command: %s", self.client, full_command)
        if not self.is_connected():
            raise RuntimeError("Ble port not open")
        # try:
        log.debug("Executing command via ble...")
        await self.client.write_gatt_char(self.command_handle, full_command)
        # sleep until response is long enough
        required_response_length = command.command_definition.construct_min_response
        timeout = 0
        while len(self.response) < required_response_length:
            timeout += 1
            if timeout >= 50:
                raise BLEResponseError(f"BLE response didnt reach len {required_response_length} in 5 seconds - got {len(self.response)}")
            #print(len(self.response))
            #print('.')
            await asyncio.sleep(0.1)
        log.debug("serial response was: %s", self.response)
        # response = self.get_protocol().check_response_and_trim(response_line)
        result = command.build_result(raw_response=self.response, protocol=self.protocol)
        self.response = bytearray()
        return result

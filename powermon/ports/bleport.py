""" bleport module ....
"""
# import serial
import asyncio
import logging
import subprocess
from time import sleep

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
from powermon.libs.config import safe_config
from powermon.libs.errors import (BLEResponseError, ConfigError,
                                  PowermonProtocolError, PowermonWIP)
from powermon.ports import PortType
from powermon.ports.abstractport import AbstractPort, _AbstractPortDTO
from powermon.protocols import get_protocol_definition
from powermon.protocols.abstractprotocol import AbstractProtocol

log = logging.getLogger("BlePort")


def ble_reset():
    try:
        subprocess.run(["bluetoothctl", "power", "off"], capture_output=True, timeout=15, check=True)
        log.info("bluetoothctl power off succeeded")
        sleep(1)
        subprocess.run(["bluetoothctl", "power", "on"], capture_output=True, timeout=15, check=True)
        log.info("bluetoothctl power on succeeded")
    except subprocess.TimeoutExpired:
        print("command timed out")
    except subprocess.CalledProcessError as exc:
        print("command execution failed")
        print(exc)
    #     outs, errs = open_blue.communicate()
    #     log.info("TimeoutExpired - outs: %s, errs: %s", outs, errs)
    # open_blue.kill()


class BlePort(AbstractPort):
    """ BlePort class - represents a BLE port - extends AbstractPort
    """

    def __str__(self):
        return f"BlePort: {self.mac=}, protocol:{self.protocol}, {self.client=}, {self.error_message=}"

    @classmethod
    async def from_config(cls, config: dict) -> 'BlePort':
        """build the BlePort object from a config dict

        Args:
            config (dict): a dict of the config for this class initialization - must include 'mac'

        Raises:
            ConfigError: Raised if something is wrong with the config

        Returns:
            BlePort: the instantiated class object
        """
        log.debug("building ble port. config:%s", safe_config(config))
        if config is None:
            raise ConfigError("BLE port config missing")
        mac = config.get("mac")
        if mac is None:
            raise ConfigError("BLE port config must include the 'mac' item")
        # get handles
        # notifier_handle = config.get("notifier_handle", 17)
        # intializing_handle = config.get("intializing_handle", 48)
        # command_handle = config.get("command_handle", 15)
        # get protocol handler, default to PI30 if not supplied
        protocol = get_protocol_definition(protocol=config.get("protocol", "PI30"))
        return cls(mac=mac, protocol=protocol)

    def __init__(self, mac, protocol: AbstractProtocol) -> None:
        self.port_type = PortType.BLE
        super().__init__(protocol=protocol)

        self.protocol.port_type = self.port_type
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

    def to_dto(self) -> _AbstractPortDTO:
        dto = _AbstractPortDTO(port_type="ble", protocol=self.protocol.to_dto())  # TODO: add correct dto
        return dto

    def _notification_callback(self, handle, data):
        log.debug("%s %s %s", handle, repr(data), len(data))
        self.response += data
        return

    def is_connected(self) -> bool:
        """is this port connected to a device?

        Returns:
            bool: True if port is defined and connected
        """
        return self.client is not None and self.client.is_connected

    async def connect(self) -> bool:
        """try to find and connect to the device identified by self.mac

        Raises:
            BleakDeviceNotFoundError: could not find or connect to the identified device
            PowermonWIP: unexpected error - signified code updates are needed

        Returns:
            bool: True if connection was successful
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
            #
            try:
                open_blue = subprocess.Popen(["bluetoothctl"], shell=True, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
                outs, errs = open_blue.communicate(b"disconnect %s\n" % self.mac.encode('utf-8'), timeout=15)
                log.info("bluetoothctlcommunicate - outs: %s, errs: %s", outs, errs)
            except subprocess.TimeoutExpired:
                outs, errs = open_blue.communicate()
                log.info("TimeoutExpired - outs: %s, errs: %s", outs, errs)
            open_blue.kill()
        log.info("ble port disconnect result, %s", self.is_connected())
        self.client = None

    async def send_and_receive(self, command: Command) -> Result:
        full_command = command.full_command
        log.debug("port: %s, full_command: %s", self.client, full_command)
        if not self.is_connected():
            raise RuntimeError("Ble port not open")
        # try:
        log.info("Executing command via ble: %s", full_command)
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

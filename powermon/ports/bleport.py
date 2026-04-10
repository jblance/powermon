"""
bleport module
- BlePort: BLE transport implementation using bleak
- ble_reset: reset bluetooth subsystem (Linux bluetoothctl)
- ble_scan: helper to discover BLE devices (and optionally list characteristics)
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
from sys import stdout
from time import sleep
from typing import Optional

try:
    from bleak import BleakClient, BleakScanner
    from bleak.exc import BleakDeviceNotFoundError
except ImportError:
    print("You are missing a python library - 'bleak'")
    print("To install it, use the below command:")
    print("    python -m pip install 'powermon[ble]'")
    print("or:")
    print("    python -m pip install bleak")
    raise

from ruamel.yaml import YAML

from powermon.commands.command import Command
from powermon.commands.result import Result
from powermon.exceptions import (
    BLEResponseError,
    ConfigError,
    PowermonProtocolError,
    PowermonWIP,
)
from powermon.protocols.abstractprotocol import AbstractProtocol

from ._types import PortType
from .port import Port

log = logging.getLogger("BlePort")


# -----------------------------------------------------------------------------
# BLE helper functions used by CLI tooling
# -----------------------------------------------------------------------------

def ble_reset() -> None:
    """
    Reset the Bluetooth subsystem via bluetoothctl (Linux).
    """
    try:
        subprocess.run(
            ["bluetoothctl", "power", "off"],
            capture_output=True,
            timeout=15,
            check=True,
        )
        log.info("bluetoothctl power off succeeded")
        sleep(1)
        subprocess.run(
            ["bluetoothctl", "power", "on"],
            capture_output=True,
            timeout=15,
            check=True,
        )
        log.info("bluetoothctl power on succeeded")
    except subprocess.TimeoutExpired:
        print("command timed out")
    except subprocess.CalledProcessError as exc:
        print("command execution failed")
        print(exc)


def ble_scan(
    *,
    details: bool = False,
    adv_data: bool = False,
    address: Optional[str] = None,
    get_chars: bool = False,
    timeout: float = 5.0,
) -> None:
    from binascii import hexlify

    async def _print_device(bledevice, advertisementdata=None) -> None:
        if address and bledevice.address.upper() != address.upper():
            return

        print(f"Name: {bledevice.name}\tAddress: {bledevice.address}")

        if not get_chars:
            return

        print("Connecting to BLE client to read characteristics/descriptors…")

        try:
            async with BleakClient(bledevice) as client:
                print("Connected:", client.is_connected)

                for service in client.services:
                    print(f"\n[Service] UUID={service.uuid} Handle={service.handle_start}-{service.handle_end}")

                    for char in service.characteristics:
                        print(
                            f"  [Characteristic] "
                            f"Handle=0x{char.handle:04X} "
                            f"UUID={char.uuid} "
                            f"Props={char.properties}"
                        )

                        # Attempt characteristic read if allowed
                        if "read" in char.properties:
                            try:
                                value = await client.read_gatt_char(char)
                                try:
                                    decoded = value.decode("ascii")
                                    print(f"    Value (ascii): {decoded}")
                                except UnicodeDecodeError:
                                    print(f"    Value (hex): {hexlify(value).decode()}")
                            except Exception as exc:
                                print(f"    Value: <read failed: {exc}>")

                        for desc in char.descriptors:
                            print(
                                f"    [Descriptor] "
                                f"Handle=0x{desc.handle:04X} "
                                f"UUID={desc.uuid}"
                            )
                            try:
                                raw = await client.read_gatt_descriptor(desc.handle)
                                try:
                                    decoded = raw.decode("ascii")
                                    print(f"      Descriptor Value (ascii): {decoded}")
                                except UnicodeDecodeError:
                                    print(f"      Descriptor Value (hex): {hexlify(raw).decode()}")
                            except Exception as exc:
                                print(f"      Descriptor Value: <read failed: {exc}>")

        except Exception as exc:
            print(f"[ERROR] Failed to connect/read device {bledevice.address}: {exc}")

    async def _scan():
        print(f"Scanning for BLE devices ({timeout}s)…")
        devices = await BleakScanner.discover(timeout=timeout, return_adv=adv_data)

        if isinstance(devices, dict):
            for bledevice, adv in devices.values():
                await _print_device(bledevice, adv)
        else:
            for bledevice in devices:
                await _print_device(bledevice)

    try:
        asyncio.run(_scan())
    except KeyboardInterrupt:
        print("BLE scan cancelled")

# -----------------------------------------------------------------------------
# BlePort implementation (runtime)
# -----------------------------------------------------------------------------

class BlePort(Port):
    """BlePort class - represents a BLE port - extends Port."""

    def __str__(self) -> str:
        return f"BlePort: mac={self.mac}, protocol={self.protocol}, client={self.client}, error={getattr(self, 'error_message', None)}"

    @classmethod
    async def from_config(cls, config, protocol, serial_number) -> "BlePort":
        """
        Build the BlePort object from a config dict.

        Args:
            config (dict): must include 'mac'
            protocol: protocol handler instance
            serial_number: unused for BLE (kept for signature consistency)

        Raises:
            ConfigError: if config is missing required items
        """
        log.debug("building ble port. config:%s", config)
        if config is None:
            raise ConfigError("BLE port config missing")
        mac = config.get("mac")
        if mac is None:
            raise ConfigError("BLE port config must include the 'mac' item")
        return cls(mac=mac, protocol=protocol)

    def __init__(self, mac: str, protocol: AbstractProtocol) -> None:
        self.port_type = PortType.BLE
        super().__init__(protocol=protocol)

        self.protocol.port_type = self.port_type
        self.mac = mac

        # set handles (from protocol; may be overridden by config in future)
        self.notifier_handle: int = getattr(self.protocol, "notifier_handle", 0)
        self.intializing_handle: int = getattr(self.protocol, "intializing_handle", 0)
        self.command_handle: int = getattr(self.protocol, "command_handle", 0)

        # Validate required handles
        if not self.notifier_handle:
            raise PowermonProtocolError(
                f"notifier_handle needs to be defined in protocol: {getattr(self.protocol, 'protocol_id', self.protocol)}"
            )
        if not self.command_handle:
            raise PowermonProtocolError(
                f"command_handle needs to be defined in protocol: {getattr(self.protocol, 'protocol_id', self.protocol)}"
            )

        self.response = bytearray()
        self.client: BleakClient | None = None
        self.error_message: str | None = None

    def _notification_callback(self, handle: int, data: bytearray) -> None:
        log.debug("%s %s %s", handle, repr(data), len(data))
        self.response += data

    def is_connected(self) -> bool:
        """Return True if connected to a BLE device."""
        return self.client is not None and self.client.is_connected

    async def connect(self) -> bool:
        """
        Find and connect to the device identified by self.mac.

        Raises:
            PowermonWIP: unexpected error; indicates more robust error handling needed
        """
        log.info("bleport connecting. mac:%s", self.mac)
        try:
            bledevice = await BleakScanner.find_device_by_address(
                device_identifier=self.mac,
                timeout=10.0,
            )
            if bledevice is None:
                raise BleakDeviceNotFoundError(f"Device with address: {self.mac} was not found.")

            log.info("got bledevice: %s", bledevice)

            self.client = BleakClient(bledevice)
            log.info("got bleclient: %s", self.client)

            await self.client.connect()
            log.info("bleclient connected")

            # enable notifications
            await self.client.start_notify(self.notifier_handle, self._notification_callback)

            # flush initializing characteristic (if provided)
            if self.intializing_handle:
                await self.client.write_gatt_char(self.intializing_handle, bytearray(b""))

        except BleakDeviceNotFoundError as exc:
            self.error_message = str(exc)
            log.error("BLE device not found: %s", exc)
            self.client = None
            return False
        except Exception as exc:
            self.error_message = str(exc)
            self.client = None
            raise PowermonWIP("connect failed") from exc

        return self.is_connected()

    async def disconnect(self) -> None:
        log.info("ble port disconnecting, %s %s", self.client, self.is_connected())
        if self.client is not None and self.client.is_connected:
            # client.disconnect can hang on some platforms; use bluetoothctl fallback
            try:
                open_blue = subprocess.Popen(
                    ["bluetoothctl"],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                )
                outs, errs = open_blue.communicate(
                    b"disconnect %s\n" % self.mac.encode("utf-8"),
                    timeout=15,
                )
                log.info("bluetoothctl communicate - outs: %s, errs: %s", outs, errs)
            except subprocess.TimeoutExpired:
                outs, errs = open_blue.communicate()
                log.info("TimeoutExpired - outs: %s, errs: %s", outs, errs)
            finally:
                open_blue.kill()

        log.info("ble port disconnect result, %s", self.is_connected())
        self.client = None

    async def send_and_receive(self, command: Command) -> Result:
        full_command = command.full_command
        log.debug("port: %s, full_command: %s", self.client, full_command)
        if not self.is_connected():
            raise RuntimeError("Ble port not open")

        log.info("Executing command via ble: %s", full_command)
        await self.client.write_gatt_char(self.command_handle, full_command)

        required_response_length = command.command_definition.construct_min_response
        timeout_ticks = 0

        while len(self.response) < required_response_length:
            timeout_ticks += 1
            if timeout_ticks >= 50:
                raise BLEResponseError(
                    f"BLE response didn't reach len {required_response_length} in 5 seconds - got {len(self.response)}"
                )
            await asyncio.sleep(0.1)

        log.debug("ble response was: %s", self.response)

        result = command.build_result(raw_response=self.response, protocol=self.protocol)
        self.response = bytearray()
        return result
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FakeDescriptor:
    handle: int
    uuid: str


@dataclass
class FakeCharacteristic:
    handle: int
    uuid: str
    properties: list[str]
    descriptors: list[FakeDescriptor]
    description: str = ""


@dataclass
class FakeService:
    uuid: str
    handle_start: int
    handle_end: int
    characteristics: list[FakeCharacteristic]


@dataclass
class FakeBLEDevice:
    name: str
    address: str
    details: dict | None = None


class FakeBleakClient:
    """
    Async context manager that mimics enough of BleakClient for ble_scan(get_chars=True).

    Exposes:
      - is_connected
      - services (iterable)
      - read_gatt_char
      - read_gatt_descriptor
    """

    def __init__(self, device):
        self.device = device
        self.is_connected = False

        self.services = [
            FakeService(
                uuid="service-1",
                handle_start=1,
                handle_end=5,
                characteristics=[
                    FakeCharacteristic(
                        handle=3,
                        uuid="char-1",
                        properties=["read"],
                        descriptors=[FakeDescriptor(handle=4, uuid="desc-1")],
                        description="Test Characteristic",
                    )
                ],
            )
        ]

    async def __aenter__(self):
        self.is_connected = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.is_connected = False

    async def read_gatt_char(self, char):
        # Return a stable byte payload
        return b"test-value"

    async def read_gatt_descriptor(self, handle: int):
        # Return a stable byte payload
        return b"\x01\x00"


class FakeFailingBleakClient(FakeBleakClient):
    async def read_gatt_descriptor(self, handle: int):
        raise PermissionError("Read not permitted")

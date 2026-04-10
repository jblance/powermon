from __future__ import annotations

import importlib
import sys
import types

import pytest

from tests.ble.fakes import FakeBLEDevice, FakeBleakClient, FakeFailingBleakClient


def _install_fake_bleak_modules(monkeypatch):
    """
    Install a minimal 'bleak' and 'bleak.exc' into sys.modules before importing bleport.
    This makes tests independent of whether bleak is installed.
    """
    bleak_mod = types.ModuleType("bleak")
    bleak_exc_mod = types.ModuleType("bleak.exc")

    class BleakDeviceNotFoundError(Exception):
        pass

    bleak_exc_mod.BleakDeviceNotFoundError = BleakDeviceNotFoundError

    class BleakScanner:
        @staticmethod
        async def discover(*, timeout=5.0, return_adv=False):
            return []

        @staticmethod
        async def find_device_by_address(*, device_identifier: str, timeout: float = 10.0):
            return None

    class BleakClient:
        def __init__(self, device):
            self.device = device
            self.is_connected = False

        async def __aenter__(self):
            self.is_connected = True
            return self

        async def __aexit__(self, exc_type, exc, tb):
            self.is_connected = False

    bleak_mod.BleakScanner = BleakScanner
    bleak_mod.BleakClient = BleakClient
    bleak_mod.exc = bleak_exc_mod

    monkeypatch.setitem(sys.modules, "bleak", bleak_mod)
    monkeypatch.setitem(sys.modules, "bleak.exc", bleak_exc_mod)


def import_bleport(monkeypatch):
    """
    Import powermon.ports.bleport after ensuring fake bleak modules exist.
    Reload if already imported to ensure it uses our injected bleak.
    """
    _install_fake_bleak_modules(monkeypatch)

    module_name = "powermon.ports.bleport"
    if module_name in sys.modules:
        return importlib.reload(sys.modules[module_name])
    return importlib.import_module(module_name)


async def fake_discover_list(*, timeout=5.0, return_adv=False):
    device = FakeBLEDevice(name="TestBLE", address="AA:BB:CC:DD:EE:FF", details={"platform": "test"})
    return [device]


async def fake_discover_dict(*, timeout=5.0, return_adv=False):
    device = FakeBLEDevice(name="TestBLE", address="AA:BB:CC:DD:EE:FF", details={"platform": "test"})
    adv = types.SimpleNamespace(
        local_name="TestBLE",
        manufacturer_data={},
        platform_data=(),
        service_data={},
        service_uuids=["service-uuid"],
        rssi=-60,
        tx_power=None,
    )
    return {device.address: (device, adv)}


async def fake_discover_two(*, timeout=5.0, return_adv=False):
    d1 = FakeBLEDevice(name="One", address="AA:AA:AA:AA:AA:AA")
    d2 = FakeBLEDevice(name="Two", address="BB:BB:BB:BB:BB:BB")
    return [d1, d2]


def test_ble_scan_basic_list(monkeypatch, capsys):
    bleport = import_bleport(monkeypatch)

    monkeypatch.setattr(bleport.BleakScanner, "discover", fake_discover_list)

    bleport.ble_scan(timeout=0.01)

    out = capsys.readouterr().out
    assert "TestBLE" in out
    assert "AA:BB:CC:DD:EE:FF" in out


def test_ble_scan_adv_data_dict(monkeypatch, capsys):
    bleport = import_bleport(monkeypatch)

    monkeypatch.setattr(bleport.BleakScanner, "discover", fake_discover_dict)

    bleport.ble_scan(timeout=0.01, adv_data=True, details=True)

    out = capsys.readouterr().out
    assert "AdvertisementData" in out
    assert "service_uuids" in out
    assert "AA:BB:CC:DD:EE:FF" in out


def test_ble_scan_address_filter(monkeypatch, capsys):
    bleport = import_bleport(monkeypatch)

    monkeypatch.setattr(bleport.BleakScanner, "discover", fake_discover_two)

    bleport.ble_scan(timeout=0.01, address="BB:BB:BB:BB:BB:BB")

    out = capsys.readouterr().out
    assert "Two" in out
    assert "BB:BB:BB:BB:BB:BB" in out
    assert "One" not in out
    assert "AA:AA:AA:AA:AA:AA" not in out


def test_ble_scan_with_characteristics_reads_descriptors(monkeypatch, capsys):
    bleport = import_bleport(monkeypatch)

    monkeypatch.setattr(bleport.BleakScanner, "discover", fake_discover_list)
    monkeypatch.setattr(bleport, "BleakClient", FakeBleakClient)

    bleport.ble_scan(timeout=0.01, get_chars=True, details=True)

    out = capsys.readouterr().out
    assert "Characteristic" in out
    assert "char-1" in out
    assert "Descriptor" in out
    assert "desc-1" in out
    # Depending on your ble_scan printing, one of these should appear
    assert "Descriptor Value" in out or "Descriptor Value" in out


def test_ble_scan_descriptor_read_failure(monkeypatch, capsys):
    bleport = import_bleport(monkeypatch)

    monkeypatch.setattr(bleport.BleakScanner, "discover", fake_discover_list)
    monkeypatch.setattr(bleport, "BleakClient", FakeFailingBleakClient)

    bleport.ble_scan(timeout=0.01, get_chars=True)

    out = capsys.readouterr().out.lower()
    assert "read failed" in out or "failed" in out

"""cli.py - hold classes for the powermon cli"""
from argparse import ArgumentParser
from platform import python_version

import yaml

from powermon.libs.version import __version__  # noqa: F401

def main():
    """main entry point for the powermon cli
    """
    description = f"Power Device Monitoring Utility CLI, version: {__version__}, python version: {python_version()}"  # pylint: disable=C0301
    parser = ArgumentParser(description=description)

    parser.add_argument("-v", "--version", action="store_true", help="Display the version")
    parser.add_argument("--bleScan", action="store_true", help="Scan for BLE devices")
    parser.add_argument("--details", action="store_true", help="Show extra BLE device data")
    parser.add_argument("--advData", action="store_true", help="Include advertisement data in BLE Scan")
    parser.add_argument("--getChars", action="store_true", help="Connect to BLE device(s) and list characteristics")
    parser.add_argument("--address", type=str, default=None, help="Only scan for supplied mac address")

    args = parser.parse_args()

    # Display version if asked
    if args.version:
        print(description)
        return None

    if args.bleScan:
        import asyncio
        from bleak import BleakClient, BleakScanner, BLEDevice

        async def print_bledevice(bledevice, advertisementdata=None, address=None, getChars=False):
            if (address is not None and bledevice.address != address.upper()):
                return
            if not args.details:
                print(f"Name: {bledevice.name}\tAddress: {bledevice.address}")
                return
            print("Name:", bledevice.name)
            print("Address:", bledevice.address)
            print("Metadata:", yaml.dump(bledevice._metadata))
            print("RSSI:", bledevice._rssi)
            print("Details:")
            print(yaml.dump(bledevice.details, default_flow_style=False))
            if advertisementdata:
                print("\tAdvertisementData:")
                print("\tlocal_name:", advertisementdata.local_name)
                print("\tmanufacturer_data:", advertisementdata.manufacturer_data)
                print("\tplatform_data:", advertisementdata.platform_data)
                print("\tservice_data:", advertisementdata.service_data)
                print("\tservice_uuids:", advertisementdata.service_uuids)
                print("\trssi:", advertisementdata.rssi)
                print("\ttx_power:", advertisementdata.tx_power)
            if getChars:
                client=BleakClient(bledevice)
                print('connecting to BLE client')
                await client.connect()
                print("Connected?", client.is_connected)
                for _int in client.services.characteristics:
                    _char =  client.services.characteristics[_int]
                    #print(yaml.dump(_char))
                    print(f"Characteristic:: Handle: {_int:02d} (0x{_int:02X}), UUID: {_char.uuid}, Description: {_char.description}, Properties: {_char.properties}")
                    for _desc in _char.descriptors:
                        #print(yaml.dump(_desc))
                        print(f"\t Descriptor:: Handle: {_desc.handle:02d} (0x{_desc.handle:02X}), UUID: {_desc.uuid}, Value: {_desc.obj['Value']}")

        async def scan_function(adv_data=False):
            print("Scanning for BLE devices")
            devices = await BleakScanner.discover(return_adv=adv_data)
            print(f"Found {len(devices)} BLE devices")
            for d in devices:
                if isinstance(d, BLEDevice):
                    # d is a BLEDevice
                    await print_bledevice(bledevice=d, address=args.address, getChars=args.getChars)
                elif isinstance(d, str):
                    # d is key to BLEDevice, Advertisement tuple
                    _bledevice, _advertisementdata = devices[d]
                    await print_bledevice(bledevice=_bledevice, advertisementdata=_advertisementdata, address=args.address, getChars=args.getChars)
                else:
                    print("unknown d")

        asyncio.run(scan_function(args.advData))

"""cli.py - hold classes for the powermon cli"""
from argparse import ArgumentParser
from platform import python_version
from sys import stdout
from pathlib import Path

#import yaml
from ruamel.yaml import YAML
# import click

from powermon.libs.version import __version__  # noqa: F401
from powermon.protocols import list_protocols, list_commands, Protocol
from powermon.outputs import list_outputs, OutputType
from powermon.libs.config import Color

def ble_scan(args):
    import asyncio
    from bleak import BleakClient, BleakScanner, BLEDevice

    async def print_bledevice(bledevice, advertisementdata=None, address=None, getChars=False):
        yaml = YAML()
        if (address is not None and bledevice.address != address.upper()):
            return
        if not args.details:
            print(f"Name: {bledevice.name}\tAddress: {bledevice.address}")
            return
        print("Name:", bledevice.name)
        print("Address:", bledevice.address)
        print("Metadata:", end="")
        yaml.dump(bledevice._metadata, stdout)
        print("RSSI:", bledevice._rssi)
        print("Details:")
        yaml.dump(bledevice.details, stdout)
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
                await print_bledevice(bledevice=d, address=args.get('address'), getChars=args.get('getChars'))
            elif isinstance(d, str):
                # d is key to BLEDevice, Advertisement tuple
                _bledevice, _advertisementdata = devices[d]
                await print_bledevice(bledevice=_bledevice, advertisementdata=_advertisementdata, address=args.get('address'), getChars=args.get('getChars'))
            else:
                print("unknown d")

    asyncio.run(scan_function(args.get('advData')))

def generate_config_file():
    print(f"{Color.WARNING}Generating config file...{Color.ENDC}")
    print("Please provide answers to the below questions [content of the square brackets are the default answer]")

    # device section
    device_name = input(f"human readible name for your device that will be monitored [unnamed]: {Color.OKBLUE}") or "unnamed"
    serial_number = input(f"{Color.ENDC}device serial number [123456789]: {Color.OKBLUE}") or "123456789"
    config = {"device": {"name": device_name, "serial_number": serial_number}}

    model =  input(f"{Color.ENDC}device model []: {Color.OKBLUE}") or None
    if model is not None:
        config['device']['model'] = model
    manufacturer = input(f"{Color.ENDC}device manufacturer []: {Color.OKBLUE}") or None
    if manufacturer is not None:
        config['device']['manufacturer'] = manufacturer

    ## port subsection
    while True:
        protocol = input(f"{Color.ENDC}Enter the protocol that your device uses (or '?' to list available protocols) [PI30]: {Color.OKBLUE}") or 'PI30'
        if protocol == '?':
            list_protocols()
            continue
        try:
            protocol_name = Protocol(protocol.lower()).name
            port_dict = {'protocol': protocol_name}
            break
        except ValueError:
            print(f"{Color.FAIL}{protocol} is not a valid protocol{Color.ENDC}")

    print(f"{Color.ENDC}please select the type of port to configure:")
    print(f"  {Color.OKGREEN}1{Color.ENDC}: test port (doesnt actually connect to any, returns test responses)")
    print(f"  {Color.OKGREEN}2{Color.ENDC}: serial port (rs232 connection, normally uses a usb<->serial adapter)")
    print(f"  {Color.OKGREEN}3{Color.ENDC}: USB port (direct USB connection to the device)")
    print(f"  {Color.OKGREEN}4{Color.ENDC}: BLE port (bluetooth low energy port)")
    port_type = input(f"Enter option number [1]: {Color.OKBLUE}") or "1"
    match port_type:
        case "2":
            print(f"{Color.OKCYAN}Serial Port selected{Color.ENDC}")
            port_dict['type'] = 'serial'
            path = input(f"{Color.ENDC}enter port path [/dev/ttyUSB0]: {Color.OKBLUE}") or "/dev/ttyUSB0"
            port_dict['path'] = path
            baud = int(input(f"{Color.ENDC}Enter the port baud rate [2400]: {Color.OKBLUE}") or 2400)
            port_dict['baud'] = baud
        case "3":
            print(f"{Color.OKCYAN}USB Port selected{Color.ENDC}")
            port_dict['type'] = 'usb'
            path = input(f"{Color.ENDC}enter port path [/dev/hidraw0]: {Color.OKBLUE}") or "/dev/hidraw0"
            port_dict['path'] = path
        case "4":
            print(f"{Color.OKCYAN}BLE Port selected{Color.ENDC}")
            port_dict['type'] = 'ble'
            while mac := input(f"{Color.ENDC}enter MAC address for BLE device (or '?' to scan devices): {Color.OKBLUE}") == '?':
                try:
                    ble_scan({})
                except FileNotFoundError:
                    print(f'{Color.FAIL}BLE Scan failed - likely BLE not functioning{Color.ENDC}')
            port_dict['mac'] = mac
        case _:
            print(f"{Color.OKCYAN}Test Port selected{Color.ENDC}")
            port_dict['type'] = 'test'
            port_dict['response_number'] = 0
    config['device']['port'] = port_dict

    # commands section
    commands = []
    while command := input(f"{Color.ENDC}Enter {Color.OKGREEN}COMMAND{Color.ENDC} (or '?' to list available commands) or press enter to end: {Color.OKBLUE}"):
        if command == '?':
            print(f"{Color.ENDC}", end='')
            list_commands(protocol=config['device']['port']['protocol'])
            continue
        if command == '':
            break
        # TODO: possible enhancement - check that command is valid for this protocol
        command_type = input(f"{Color.ENDC}Choose the command type:\n  {Color.OKGREEN}b{Color.ENDC}: 'basic'\n  {Color.OKGREEN}t{Color.ENDC}: 'templated'\n  [b]: {Color.OKBLUE}")
        if command_type.lower().startswith('t'):
            command_type = 'templated'
        else:
            command_type = 'basic'
        # add outputs
        outputs = []
        while output := input(f"  {Color.ENDC}Enter {Color.OKGREEN}OUTPUT{Color.ENDC} to use (or '?' to list available outputs) or press enter to end: {Color.OKBLUE}"):
            if output == '?':
                print(f"{Color.ENDC}", end='')
                list_outputs()
                continue
            if output == '':
                break
            try:
                output_name = OutputType(output.lower()).value
                # TODO: get formatter
                outputs.append({'type': output_name, 'format': 'simple'})
            except ValueError:
                print(f"{Color.FAIL}{output} is not a valid output type{Color.ENDC}")
        if not outputs:
            print(f'{Color.OKCYAN}No outputs added, adding default{Color.ENDC}')
            outputs.append({'type': 'screen', 'format': 'table'})
        print(f'{Color.OKCYAN}Adding command: {command}{Color.ENDC}')
        commands.append({'command': command, 'type': command_type, 'outputs': outputs})
    if not commands:
        print(f"{Color.OKCYAN}No commands selected - adding default command{Color.ENDC}")
        commands.append({'command': 'default', 'type': 'basic', 'outputs': [{'type': 'screen', 'format': 'table'}]})
    config['commands'] = commands

    # mqttbroker section
    mqtt_dict = {}
    brokername = input(f"{Color.ENDC}Enter the mqttbroker name or press enter to skip this section [skip section]: {Color.OKBLUE}")
    if brokername:
        mqtt_dict['name'] = brokername
        mqtt_port = int(input(f"{Color.ENDC}Enter mqttbroker port [1833]: {Color.OKBLUE}") or 1833)
        mqtt_dict['port'] = mqtt_port
        mqtt_user = input(f"{Color.ENDC}Enter mqtt broker username [None]: {Color.OKBLUE}") or None
        mqtt_dict['username'] = mqtt_user
        if mqtt_user is None:
            mqtt_pass = None
        else:
            mqtt_pass = input(f"{Color.ENDC}Enter mqtt broker user password [None]: {Color.OKBLUE}") or None
        mqtt_dict['password'] = mqtt_pass
        adhoc_topic = input(f"{Color.ENDC}Enter mqtt broker adhoc command listening topic [powermon/adhoc_commands]: {Color.OKBLUE}") or 'powermon/adhoc_commands'
        mqtt_dict['adhoc_topic'] = adhoc_topic
        adhoc_result_topic = input(f"{Color.ENDC}Enter mqtt broker adhoc command listening topic [powermon/adhoc_commands]: {Color.OKBLUE}") or 'powermon/adhoc_results'
        mqtt_dict['adhoc_result_topic'] = adhoc_result_topic
    if mqtt_dict:
        config['mqttbroker'] = mqtt_dict
    else:
        print(f'{Color.OKCYAN}Skipping mqttbroker section{command}{Color.ENDC}')

    # api: None | APIConfig = Field(default=None)
    # TODO: add api section

    # daemon section
    daemon_dict = {}
    daemon_type = input(f"{Color.ENDC}Select a daemon type or press enter to skip\n  {Color.OKGREEN}1{Color.ENDC}: systemd\n  {Color.OKGREEN}2{Color.ENDC}: initd\nEnter option number [skip section]: {Color.OKBLUE}")
    match daemon_type:
        case '':
            print(f'{Color.OKCYAN}Skipping daemon section{command}{Color.ENDC}')
        case 1 | '1' | 's':
            daemon_dict['type'] = 'systemd'
            try:
                keepalive = input(f"{Color.ENDC}End keepalive in seconds [60]: {Color.OKBLUE}") or 60
                keepalive = int(keepalive)
            except ValueError:
                print(f"{Color.FAIL}Invalid input for an int: {keepalive}{Color.ENDC} - defaulting to: 60")
                keepalive = 60
            daemon_dict['keepalive'] = keepalive
        case 2 | '2' | 'i':
            daemon_dict = {'type': 'initd'}
    if daemon_dict:
        config['daemon'] = daemon_dict

    # debug section
    debuglevel = input(f"{Color.ENDC}Enter the debuglevel (DEBUG, INFO, WARNING, ERROR, CRITICAL) or press enter to ignore [skip section]: {Color.OKBLUE}")
    if debuglevel.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        config['debuglevel'] = debuglevel.upper()
    else:
        print(f'{Color.OKCYAN}Skipping debug section{command}{Color.ENDC}')

    # loop section
    loop = input(f"{Color.ENDC}Enter the delay in seconds between each command processing loop or 'once' for a single pass [once]: {Color.OKBLUE}") or "once"
    if loop != 'once':
        try:
            loop = int(loop)
        except ValueError:
            print(f"{Color.FAIL}Could not parse {loop} to an int, defaulting to 'once{Color.ENDC}")
            loop = 'once'
    config['loop'] = loop

    filename = input(f"{Color.ENDC}Enter filename to write config to or 'screen' to dump to screen [screen]: {Color.OKBLUE}") or 'screen'
    yaml = YAML()
    if filename == 'screen':
        output = stdout
    else:
        output = Path(filename)
    print(f"\n{Color.WARNING}Dumping config yaml....{Color.ENDC}")
    yaml.dump(config, output)



def main():
    """main entry point for the powermon cli
    """
    description = f"Power Device Monitoring Utility CLI, version: {__version__}, python version: {python_version()}"  # pylint: disable=C0301
    parser = ArgumentParser(description=description)

    parser.add_argument("-v", "--version", action="store_true", help="Display the version")
    parser.add_argument("-g", "--generateConfigFile", action="store_true", help="Generate Config File")
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
        ble_scan(args)
        return

    if args.generateConfigFile:
        try:
            generate_config_file()
        except KeyboardInterrupt:
            print(f"{Color.FAIL}Generation of config file aborted{Color.ENDC}")
    
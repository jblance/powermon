"""cli.py - hold classes for the powermon cli"""
import gettext
from argparse import ArgumentParser
from pathlib import Path
from platform import python_version
from sys import stdout

from deepdiff import DeepDiff
#import yaml
from ruamel.yaml import YAML

from powermon import _

from powermon.libs.config import Color
from powermon.libs.errors import CommandDefinitionMissing, ConfigError
from powermon.libs.version import __version__  # noqa: F401
from powermon.outputformats import FormatterType, get_formatter, list_formats
from powermon.outputs import OutputType, list_outputs
from powermon.ports.bleport import ble_reset
from powermon.protocols import (Protocol, get_protocol_definition,
                                list_commands, list_protocols)



def ble_scan(args):
    """ scan for BLE devices """
    import asyncio

    from bleak import BleakClient, BleakScanner, BLEDevice

    async def print_bledevice(bledevice, advertisementdata=None, address=None, get_chars=False):
        yaml = YAML()
        if (address is not None and bledevice.address != address.upper()):
            return
        if not args.details:
            print(f"Name: {bledevice.name}\tAddress: {bledevice.address}")
            return
        print("Name:", bledevice.name)
        print("Address:", bledevice.address)
        print("Metadata:", end="")
        yaml.dump(bledevice._metadata, stdout)  # pylint: disable=W0212
        print("RSSI:", bledevice._rssi)  # pylint: disable=W0212
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
        if get_chars:
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
                await print_bledevice(bledevice=d, address=args.address, get_chars=args.getChars)
            elif isinstance(d, str):
                # d is key to BLEDevice, Advertisement tuple
                _bledevice, _advertisementdata = devices[d]
                await print_bledevice(bledevice=_bledevice, advertisementdata=_advertisementdata, address=args.address, get_chars=args.getChars)
            else:
                print("unknown d")

    asyncio.run(scan_function(args.advData))

def generate_config_file():
    """ generate a config file from the answer to questions """
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
    port_dict = {}
    # port type
    print(f"{Color.ENDC}please select the {Color.OKGREEN}PORT TYPE{Color.ENDC} to configure:")
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
    # protocol
    while True:
        protocol = input(f"{Color.ENDC}Enter the {Color.OKGREEN}PROTOCOL{Color.ENDC} that your device uses (or '?' to list available protocols) [PI30]: {Color.OKBLUE}") or 'PI30'
        if protocol == '?':
            list_protocols()
            continue
        try:
            protocol_name = Protocol(protocol.lower()).name
            port_dict['protocol'] = protocol_name
            break
        except ValueError:
            print(f"{Color.FAIL}{protocol} is not a valid protocol{Color.ENDC}")
    config['device']['port'] = port_dict

    # commands section
    commands = []
    while command := input(f"{Color.ENDC}Enter {Color.OKGREEN}COMMAND ({len(commands)+1}){Color.ENDC} (or '?' to list available commands) or press enter to end: {Color.OKBLUE}"):
        if command == '?':
            print(f"{Color.ENDC}", end='')
            list_commands(protocol=config['device']['port']['protocol'])
            continue
        if command == '':
            break
        # check that command is valid for this protocol
        proto = get_protocol_definition(protocol=protocol_name)
        try:
            proto.get_command_definition(command=command)
        except CommandDefinitionMissing:
            print(f'{Color.FAIL}Invalid command: {command} for protocol: {protocol_name}{Color.ENDC}')
            continue
        # Currently disabled - templated commands need to be manually edited
        # command_type = input(f"{Color.ENDC}Choose the command type for {command}:\n  {Color.OKGREEN}b{Color.ENDC}: 'basic'\n  {Color.OKGREEN}t{Color.ENDC}: 'templated'\n  [b]: {Color.OKBLUE}")
        # if command_type.lower().startswith('t'):
        #     command_type = 'templated'
        # else:
        #     command_type = 'basic'
        command_type = 'basic'
        # add trigger
        trigger_dict = {}
        while trigger := input(f"{Color.ENDC}Select {Color.OKGREEN}TRIGGER{Color.ENDC} for {command}\n{Color.OKGREEN}1{Color.ENDC}: EVERY (trigger every XX seconds)\n{Color.OKGREEN}2{Color.ENDC}: LOOPS (trigger every X loops)\n{Color.OKGREEN}3{Color.ENDC}: AT (trigger at specified time HH:MM)\nEnter option number [1]: {Color.OKBLUE}") or 1:
            match trigger:
                case None | "" | 1 | "1":
                    value = int(input(f"{Color.ENDC}Enter number of seconds between command runs (may be overridden by overall loop delay) [5]: {Color.OKBLUE}") or 5)
                    trigger_dict['every'] = value
                    break
                case 2 | "2":
                    value = int(input(f"{Color.ENDC}Enter number loops between each command run [1]: {Color.OKBLUE}") or 1)
                    trigger_dict['loops'] = value
                    break
                case 3 | "3":
                    value = input(f"{Color.ENDC}Enter time (as HH:MM 24hour format) for command to run: {Color.OKBLUE}")
                    trigger_dict['at'] = value
                    break
                case _:
                    print(f"Invalid option {trigger}")
                    continue
        # add outputs
        outputs = []
        while output := input(f"{Color.ENDC}Enter {Color.OKGREEN}OUTPUT ({len(outputs)+1}){Color.ENDC} to use for {command} (or '?' to list available outputs) or press enter to end: {Color.OKBLUE}"):
            if output == '?':
                print(f"{Color.ENDC}", end='')
                list_outputs()
                continue
            if output == '':
                break
            try:
                output_name = OutputType(output.lower()).value
                # add formatter
                while formatter := input(f"{Color.ENDC}Enter {Color.OKGREEN}FORMATTER{Color.ENDC} (or '?' to list available formatter) [simple]: {Color.OKBLUE}") or 'simple':
                    if formatter == '?':
                        print(f"{Color.ENDC}", end='')
                        list_formats()
                        continue
                    try:
                        format_name = FormatterType(formatter.lower()).value
                        # add all format options with defaults
                        fmt = get_formatter(format_name)
                        fmt_options = {'type': format_name}
                        fmt_options.update(fmt({}).get_options())
                        output_dict = {'type': output_name, 'format': fmt_options}
                        #output_dict.update(fmt_options)
                        outputs.append(output_dict)
                        print(f"{Color.OKCYAN}Added formatter: {format_name}{Color.ENDC}")
                        break
                    except ValueError:
                        print(f'{Color.FAIL}Invalid formatter: {formatter}{Color.ENDC}')
            except ValueError:
                print(f"{Color.FAIL}{output} is not a valid output type{Color.ENDC}")
        if not outputs:
            print(f'{Color.OKCYAN}No outputs added, adding default{Color.ENDC}')
            outputs.append({'type': 'screen', 'format': 'table'})
        print(f'{Color.OKCYAN}Adding command: {command}{Color.ENDC}')
        commands.append({'command': command, 'type': command_type, 'trigger': trigger_dict, 'outputs': outputs})
    if not commands:
        print(f"{Color.OKCYAN}No commands selected - adding default command{Color.ENDC}")
        commands.append({'command': 'default', 'type': 'basic', 'trigger': {'loops': 1}, 'outputs': [{'type': 'screen', 'format': 'table'}]})
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
        adhoc_topic = input(f"{Color.ENDC}Enter mqtt broker adhoc command {Color.OKGREEN}listening{Color.ENDC} topic [powermon/adhoc_commands]: {Color.OKBLUE}") or 'powermon/adhoc_commands'
        mqtt_dict['adhoc_topic'] = adhoc_topic
        adhoc_result_topic = input(f"{Color.ENDC}Enter mqtt broker adhoc command {Color.OKGREEN}results{Color.ENDC} topic [powermon/adhoc_commands]: {Color.OKBLUE}") or 'powermon/adhoc_results'
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

def show_command_definition_differences(p1, p2):
    """ function to compare a single command in 2 different protocols """
    p1_color = Color.OKBLUE
    p2_color = Color.OKCYAN
    fields = ['description', 'help_text', 'category', 'result_type', 'regex', 'aliases', 'command_type', 'command_code', 'command_data', 'construct', 'construct_min_response', ]
    field_width = 35
    data_width = 60

    for field in fields:
        p1_field = getattr(p1, field, "")
        p2_field = getattr(p2, field, "")
        p1_field = "" if p1_field is None else str(p1_field)
        p2_field = "" if p2_field is None else str(p2_field)

        if p1_field == p2_field:
            #print(f"|{field:>{field_width}}|{p1_field:^{data_width*2+1}}|")
            print(f"|{field:>{field_width}}|{p1_field:>{data_width}}|{p2_field:<{data_width}}|")
            # print(f"{field} matches in both protocols")
        elif not p1_field and p2_field:
            print(f"|{Color.FAIL}{field:>{field_width}}{Color.ENDC}|{p1_color}{'Not Present':>{data_width}}{Color.ENDC}|{p2_color}{str(p2_field):<{data_width}}{Color.ENDC}|")
        elif not p2_field and p1_field:
            print(f"|{Color.FAIL}{field:>{field_width}}{Color.ENDC}|{p1_color}{str(p1_field):>{data_width}}{Color.ENDC}|{p2_color}{'Not Present':<{data_width}}{Color.ENDC}|")
        else:
            print(f"|{Color.FAIL}{field:>{field_width}}{Color.ENDC}|{p1_color}{p1_field:>{data_width}}{Color.ENDC}|{p2_color}{p2_field:<{data_width}}{Color.ENDC}|")

    p1_tests = getattr(p1, 'test_responses', "")
    p2_tests = getattr(p2, 'test_responses', "")
    if len(p1_tests) == len(p2_tests):
        print(f"|{'test_responses (count)':>{field_width}}|{len(p1_tests):>{data_width}}|{len(p2_tests):<{data_width}}|")
    else:
        print(f"|{Color.FAIL}{'test_responses (count)':>{field_width}}{Color.ENDC}|{len(p1_tests):>{data_width}}|{len(p2_tests):<{data_width}}|")

    # 'reading_definitions',
    if p1.reading_definition_count() == p2.reading_definition_count():
        print(f"|{'reading_definitions (count)':>{field_width}}|{p1.reading_definition_count():>{data_width}}|{p2.reading_definition_count():<{data_width}}|")
    else:
        print(f"|{Color.FAIL}{'reading_definitions (count)':>{field_width}}{Color.ENDC}|{p1.reading_definition_count():>{data_width}}|{p2.reading_definition_count():<{data_width}}|")
    for i in range(min(p1.reading_definition_count(), p2.reading_definition_count())):
        p1_rd = p1.reading_definitions[i]
        # print(p1_rd)
        # return
        p2_rd = p2.reading_definitions[i]
        field_name = f"rd[{i}]: {getattr(p1_rd, 'description')}"[:field_width]
        if p1_rd == p2_rd:
            print(f"|{field_name:>{field_width}}|{'Matches':>{data_width}}|{'':<{data_width}}|")
        else:
            for item in ['description', 'response_type', 'unit', 'default', 'format_template', 'icon', 'device_class']:
                #'options'
                if getattr(p1_rd, item) == getattr(p2_rd, item):
                    pass
                else:
                    message = f"{Color.WARNING}{item}{Color.ENDC}: {getattr(p1_rd, item)}"
                    print(f"|{Color.FAIL}{field_name:>{field_width}}{Color.ENDC}|{message:>{data_width+9}}|{getattr(p2_rd, item)}")
            if getattr(p1_rd, 'options') != getattr(p2_rd, 'options'):
                print(f"|{Color.FAIL}{field_name:>{field_width}}{Color.ENDC}|{'options differ':>{data_width}}|{' ':<{data_width}}|")
    if p1.reading_definition_count() > p2.reading_definition_count():
        for i in range(p2.reading_definition_count(), p1.reading_definition_count()):
            field_name = f"reading_definition[{i}]"
            print(f"|{Color.FAIL}{field_name:>{field_width}}{Color.ENDC}|{p1_color}{'Added':>{data_width}}{Color.ENDC}|{' ':<{data_width}}|")
    if p1.reading_definition_count() < p2.reading_definition_count():
        for i in range(p1.reading_definition_count(), p2.reading_definition_count()):
            field_name = f"reading_definition[{i}]"
            print(f"|{Color.FAIL}{field_name:>{field_width}}{Color.ENDC}|{'':>{data_width}}|{p1_color}{'Added':<{data_width}}{Color.ENDC}|")
    # self.reading_definitions: dict[int | str, ReadingDefinition] = reading_definitions

def compare_protocols(protocols):
    """ function to compare 2 protocols """
    p1_color = Color.OKBLUE
    p2_color = Color.OKCYAN
    if protocols.find(',') <= 0:
        print('need to supply 2 comma separated protocols, eg: "pi30,pi30max" ')
        return
    _proto_1, _proto_2 = protocols.split(',')
    limit_to_single_command = False
    _cmd = None
    if _proto_2.find(':') > 0:
        _proto_2, _cmd = _proto_2.split(':')
        limit_to_single_command = True
    try:
        proto_1 = get_protocol_definition(_proto_1)
        proto_2 = get_protocol_definition(_proto_2)
    except ConfigError as ex:
        print(f'ERROR: {ex}')
        return
    print(f"\n{Color.BOLD}=====================\n PROTOCOL COMPARISON\n====================={Color.ENDC}")
    if limit_to_single_command:
        print(f"Checking command: {Color.HEADER}{_cmd}{Color.ENDC}")
        print(f"{p1_color}Defined in {_proto_1}{Color.ENDC}: {_cmd in proto_1.command_definitions}")
        print(f"{p2_color}Defined in {_proto_2}{Color.ENDC}: {_cmd in proto_2.command_definitions}")
        if _cmd in proto_1.command_definitions and _cmd in proto_2.command_definitions:
            p1 = proto_1.command_definitions[_cmd]
            p2 = proto_2.command_definitions[_cmd]
            show_command_definition_differences(p1, p2)

        return
    same_commands = []
    diff_commands = []
    for _command in (proto_2.command_definitions.keys() & proto_1.command_definitions.keys()):
        _diff = DeepDiff(proto_1.command_definitions[_command], proto_2.command_definitions[_command], ignore_order=True, ignore_encoding_errors=True)
        if not _diff:
            same_commands.append(_command)
            # print(f"P1 and P2 are the same for {_command}")
        else:
            diff_commands.append(_command)

    print(f"{p1_color}{_proto_1} has {len(proto_1.command_definitions)} commands{Color.ENDC}\n{p2_color}{_proto_2} has {len(proto_2.command_definitions)} commands{Color.ENDC}")
    print(f"Commands with the same definition in both protocols ({len(same_commands)})\n\t{same_commands}")
    print(f"Commands in {_proto_2} but not {_proto_1} ({len(proto_2.command_definitions.keys() - proto_1.command_definitions.keys())})\n\t{p2_color}{proto_2.command_definitions.keys() - proto_1.command_definitions.keys()}{Color.ENDC}")
    print(f"Commands in {_proto_1} but not {_proto_2} ({len(proto_1.command_definitions.keys() - proto_2.command_definitions.keys())})\n\t{p1_color}{proto_1.command_definitions.keys() - proto_2.command_definitions.keys()}{Color.ENDC}")
    print(f"Commands in both protocols with different config ({len(diff_commands)})\n\t{diff_commands}")
    for _command in diff_commands:
        p1 = proto_1.command_definitions[_command]
        p2 = proto_2.command_definitions[_command]
        print(f"\n{Color.HEADER}{_command}{Color.ENDC}")
        show_command_definition_differences(p1, p2)

def main():
    """main entry point for the powermon cli
    """
    transl_name = _('Power Device Monitoring Utility CLI')
    description = f"{transl_name}, version: {__version__}, python version: {python_version()}"  # pylint: disable=C0301
    parser = ArgumentParser(description=description)

    parser.add_argument("-v", "--version", action="store_true", help="Display the version")
    parser.add_argument("-g", "--generateConfigFile", action="store_true", help="Generate Config File")
    parser.add_argument("--listProtocols", action="store_true", help="List available protocols")
    parser.add_argument("--listCommands",type=str, metavar='PROTOCOL', help="List available commands for PROTOCOL")
    parser.add_argument("--listFormats", action="store_true", help="List available output formats")
    parser.add_argument("--listOutputs", action="store_true", help="List available output modules")
    parser.add_argument("--compareProtocols", type=str, default=None, metavar='PROTO1,PROTO2[:CMD]', help="Compare 2 protocol definitions (comma separated) with optional CMD to only compare that command")
    parser.add_argument("--bleReset", action="store_true", help="Reset the bluetooth subsystem (power off / on bluetoothctl)")
    parser.add_argument("--bleScan", action="store_true", help="Scan for BLE devices")
    parser.add_argument("--details", action="store_true", help="Show extra BLE device data")
    parser.add_argument("--advData", action="store_true", help="Include advertisement data in BLE Scan")
    parser.add_argument("--getChars", action="store_true", help="Connect to BLE device(s) and list characteristics")
    parser.add_argument("--address", type=str, metavar='MAC', default=None, help="Only scan for supplied mac address")

    args = parser.parse_args()

    # Display version if asked
    if args.version:
        print(description)
        return None

    if args.listProtocols:
        list_protocols()
        return None

    if args.listCommands:
        list_commands(args.listCommands)
        return None

    if args.listFormats:
        list_formats()
        return None

    if args.listOutputs:
        list_outputs()
        return None

    if args.bleReset:
        ble_reset()
        return

    if args.bleScan:
        ble_scan(args)
        return

    if args.compareProtocols:
        compare_protocols(args.compareProtocols)
        return

    if args.generateConfigFile:
        try:
            generate_config_file()
        except KeyboardInterrupt:
            print(f"{Color.FAIL}Generation of config file aborted{Color.ENDC}")
    

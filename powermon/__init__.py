# !/usr/bin/python3
from argparse import ArgumentParser
import importlib
import logging
from sys import exit

from .version import __version__  # noqa: F401
# from powermon.io.hidrawio import HIDRawIO

log = logging.getLogger('powermon')
# setup logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# set default log levels
log.setLevel(logging.WARNING)
logging.basicConfig()


def main():
    parser = ArgumentParser(description=f'Power Monitor Utility, version: {__version__}')
    parser.add_argument('-n', '--name', type=str, help='Specifies the device name - used to differentiate different devices', default='noname')
    parser.add_argument('-t', '--type', type=str, help='Specifies the device type (mppsolar [default], jkbms)', default='mppsolar')
    parser.add_argument('-p', '--port', type=str, help='Specifies the device communication port, (/dev/ttyUSB0 [default], /dev/hidraw0, test ...)', default='/dev/ttyUSB0')
    parser.add_argument('-P', '--protocol', type=str, help='Specifies the device command and response protocol, (default: PI30)', default='PI30')
    parser.add_argument('-c', '--command', help='Raw command to run')
    parser.add_argument('-R', '--show_raw', action='store_true', help='Display the raw results')
    parser.add_argument('-o', '--output', type=str, help='Specifies the output processor(s) to use [comma separated if multiple] (screen [default], influx_mqtt, mqtt, hass_config, hass_mqtt)', default='screen')
    parser.add_argument('-q', '--mqtt_broker', type=str, help='Specifies the mqtt broker to publish to if using a mqtt output (localhost [default], hostname, ip.add.re.ss ...)', default='localhost')
    parser.add_argument('-T', '--tag', type=str, help='Override the command name and use this instead (for mqtt and influx type output processors)')
    parser.add_argument('-D', '--enable_debug', action='store_true', help='Enable Debug and above (i.e. all) messages')
    parser.add_argument('-I', '--enable_info', action='store_true', help='Enable Info and above level messages')
    args = parser.parse_args()

    # Turn on debug if needed
    if(args.enable_debug):
        log.setLevel(logging.DEBUG)
    elif(args.enable_info):
        log.setLevel(logging.INFO)

    log.info(f'Powermon version {__version__}')
    # create instance of device (supplying port + protocol types)
    log.info(f'Creating device "{args.name}" (type: "{args.type}") on port "{args.port}" using protocol "{args.protocol}"')
    device_type = args.type.lower()
    try:
        device_module = importlib.import_module('powermon.devices.' + device_type, '.')
    except ModuleNotFoundError:
        # perhaps raise a Powermon exception here??
        log.critical(f'No module found for device {device_type}')
        exit(1)
    device_class = getattr(device_module, device_type)
    log.debug(f'device_class {device_class}')
    # The device class __init__ will instantiate the port communications and protocol classes
    device = device_class(name=args.name, port=args.port, protocol=args.protocol)

    # run command or called helper function
    results = device.run_command(command=args.command, show_raw=args.show_raw)

    if args.tag:
        tag = args.tag
    else:
        tag = args.command
    if args.mqtt_broker:
        mqtt_broker = args.mqtt_broker
    else:
        args.mqtt_broker = 'localhost'
    # send to output processor(s)
    outputs = args.output.split(',')
    for output in outputs:
        log.info(f'attempting to create output processor: {output}')
        try:
            output_module = importlib.import_module('powermon.outputs.' + output, '.')
        except ModuleNotFoundError:
            # perhaps raise a Powermon exception here??
            log.critical(f'No module found for output processor {output}')
        output_class = getattr(output_module, output)

        # init function will do the processing
        output_class(results=results, tag=tag, mqtt_broker=mqtt_broker)

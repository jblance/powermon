# Power Monitoring Python Package

_Note: python2 not supported_

Python package with reference library of commands (and responses)
for Power Monitoring Devices, e.g.:
MPP-Solar inverters - aka:
- PIP-4048MS
- IPS-4000WM
- Voltronic Axpert MKS 5KVA Off-grid Inverter-Chargers
- LV5048

JKBMS Battery Monitoring Devices, e.g.:
- JK-B1A24S
- JK-B2A24S


## Usage ##
### Install ###
* ```python ./setup.py install```

### Run without installing ###

*  With INFO messages: ```python -c 'import powermon; powermon.main()' -I```

### Options ###
```
$ powermon -h
usage: powermon [-h] [-n NAME] [-t TYPE] [-p PORT] [-P PROTOCOL] [-c COMMAND]
                [-R] [-o OUTPUT] [-q MQTT_BROKER] [-T TAG] [-D] [-I]

Power Monitor Utility, version: 0.1.2

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Specifies the device name - used to differentiate
                        different devices
  -t TYPE, --type TYPE  Specifies the device type (mppsolar [default], jkbms)
  -p PORT, --port PORT  Specifies the device communication port, (/dev/ttyUSB0
                        [default], /dev/hidraw0, test ...)
  -P PROTOCOL, --protocol PROTOCOL
                        Specifies the device command and response protocol,
                        (default: PI30)
  -c COMMAND, --command COMMAND
                        Raw command to run
  -R, --show_raw        Display the raw results
  -o OUTPUT, --output OUTPUT
                        Specifies the output processor(s) to use [comma
                        separated if multiple] (screen [default], influx_mqtt,
                        mqtt, hass_config, hass_mqtt)
  -q MQTT_BROKER, --mqtt_broker MQTT_BROKER
                        Specifies the mqtt broker to publish to if using a
                        mqtt output (localhost [default], hostname,
                        ip.add.re.ss ...)
  -T TAG, --tag TAG     Override the command name and use this instead (for
                        mqtt and influx type output processors)
  -D, --enable_debug    Enable Debug and above (i.e. all) messages
  -I, --enable_info     Enable Info and above level messages
```

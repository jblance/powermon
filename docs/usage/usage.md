## Installation

powermon is packaged on pypi. 

There are a number of optional dependancies that can be installed based on the usage required. It is suggested to not install the extras unless needed

``` console title='pip install examples'
user@host:~ $ pip install powermon           # minimal install
user@host:~ $ pip install powermon[api]      # include web api dependancies
user@host:~ $ pip install powermon[ble]      # include bluetooth dependancies
user@host:~ $ pip install powermon[modbus]   # include modbus dependancies
user@host:~ $ pip install powermon[systemd]  # include systemd dependancies
user@host:~ $ pip install powermon[ble,dev]  # include bluetooth and development dependencies

user@host:~ $ pip install powermon[dev]      # include all development dependancies
```

## Powermon Command

powermon requires a config file, and the simplest usage is: 

    powermon -C /path/to/configfile.yaml

Note: Config file syntax is described in [config file](config_file.md)

### Powermon Command Options

As well as the location of the config file, several other command options are available to customise usage.

To check available options use the help option `-h`
```
$ powermon -h
usage: powermon [-h] [-C [CONFIGFILE]] [--config CONFIG] [-V] [-v] [--listProtocols] [--listCommands PROTOCOL] [-1] [--force] [-I] [-D] [-a COMMAND]

Power Device Monitoring Utility, version: 1.0.14-dev, python version: 3.11.7

options:
    -h, --help            show this help message and exit
    -C [CONFIGFILE], --configFile [CONFIGFILE]
                          Full location of config file
    --config CONFIG       Supply config items on the commandline in json format, eg '{"device": {"port":{"type":"test"}}, "commands": [{"command":"QPI"}]}'
    -V, --validate        Validate the configuration
    -v, --version         Display the version
    --listProtocols       Display the currently supported protocols
    --listCommands PROTOCOL
                          Display available commands for PROTOCOL
    -1, --once            Only loop through config once
    --force               Force commands to run even if wouldnt be triggered (should only be used with --once)
    -I, --info            Enable Info and above level messages
    -D, --debug           Enable Debug and above (i.e. all) messages
    -a COMMAND, --adhoc COMMAND
                          Send adhoc command to mqtt adhoc command queue - needs config file specified and populated
```

### Run Adhoc Command

``` console
$ powermon -C powermon.yaml -a device_info
```

There are 2 scenarios to running an adhoc command:

1. The device is not currently connected to a powermon process/service
   - This still requires a config file to provide the details, but the `-a` flag will ignore all commands in the config file an only run the supplied command
2. The device is actively being monitored by (for example) a powermon service instance
   - this will attempt to send the command via mqtt, so will not work if there is no accessible mqtt broker

### List Available Protocols

``` console title="Supported Protocols"
$ powermon --listProtocols
Power Device Monitoring Utility, version: 1.0.14-dev, python version: 3.11.7
Supported protocols
PI18: PI18 protocol handler
PI30: PI30 protocol handler
PI30MAX: PI30 protocol handler for LV6048MAX and similar inverters
DALY: DALY protocol handler for DALY BMS
NEEY: NEEY Active Balancer protocol handler
HELTEC: Heltec Active Balancer protocol handler
VED: VED protocol handler for Victron direct SmartShunts
JKSERIAL: JKBMS TTL serial communication protocol handler
```

### List Available Commands for a Protocol


``` console
$ powermon --listCommands neey
Power Device Monitoring Utility, version: 1.0.14-dev, python version: 3.11.7
Commands in protocol: NEEY
info ['device_info'] - get the balancer information 
cell_info  - get the cell voltage, resistance information as well as battery voltage and balancing current 
defaults ['factory_defaults'] - get the factory default settings 
settings ['get_settings'] - get the bms settings 
on ['balancer_on'] - turn balancer on 
off ['balancer_off'] - turn balancer off 
cell_count  - set the number of cells in the battery   -- eg cell_count=4 (set cell count to 4)
```
## Powermon CLI

So far there are several uses for the ``powermon-cli`` command

* list the available protocols
```
powermon-cli --listProtocols
```
* List available commands in a given protocol
```
powermon-cli --listCommands PI30
```
* List available output modules
```
powermon-cli --listOutputs
```
* List available output formats
```
powermon-cli --listFormats
```
* generating a config file starter from the answers of a series of questions
```
powermon-cli -g
```
* compare two protocols (and optionally a single command in each protocol) 
```
powermon-cli --compareProtocols pi30,pi30max  # (compare the pi30 and pi30max protocols)
powermon-cli --compareProtocols pi30,pi30max:QMOD  # (compare the QMOD command from the pi30 and pi30max protocols)
```
* scan for details of BLE devices (with options to show additional details) 
   `powermon-cli --bleScan --details --advData --getChars`


### Command Options

```
$ powermon-cli -h
usage: powermon-cli [-h] [-v] [-g] [--listProtocols] [--listCommands PROTOCOL] [--listFormats] [--listOutputs] [--compareProtocols PROTO1,PROTO2] [--bleReset] [--bleScan] [--details] [--advData] [--getChars] [--address MAC]

Power Device Monitoring Utility CLI, version: 1.0.16-dev, python version: 3.11.7

options:
-h, --help            show this help message and exit
-v, --version         Display the version
-g, --generateConfigFile
                      Generate Config File
--listProtocols       List available protocols
--listCommands PROTOCOL
                      List available commands for PROTOCOL
--listFormats         List available output formats
--listOutputs         List available output modules
--compareProtocols PROTO1,PROTO2[:CMD]
                      Compare 2 protocol definitions (comma separated) with optional CMD to only compare that command
--bleReset            Reset the bluetooth subsystem (power off / on bluetoothctl)
--bleScan             Scan for BLE devices
--details             Show extra BLE device data
--advData             Include advertisement data in BLE Scan
--getChars            Connect to BLE device(s) and list characteristics
--address MAC         Only scan for supplied mac address
```

### List Protocols


```
$ powermon-cli --listProtocols
Supported protocols
PI18: PI18 protocol handler
PI30: PI30 protocol handler
PI30MAX: PI30 protocol handler for LV6048MAX and similar inverters
PI30MST: PI30 protocol handler for PIP4048MST and similar inverters
DALY: DALY protocol handler for DALY BMS
NEEY: NEEY Active Balancer protocol handler
HELTEC: NEEY Active Balancer protocol handler
VED: VED protocol handler for Victron direct SmartShunts
JKSERIAL: JKBMS TTL serial communication protocol handler
```

### List Commands in a protocol

```
$ powermon-cli --listCommands PI30
Commands in protocol: PI30
QPI  - Get the Inverter supported Protocol ID 
QID ['get_id', 'default'] - Get the Serial Number of the Inverter 
QVFW  - Get the Main CPU firmware version 
QVFW2  - Get the Secondary CPU firmware version 
QBOOT  - Get DSP Has Bootstrap 
QDI  - Get the Inverters Default Settings 
QMN  - Get the Model Name 
PGR  - Set Grid Working Range  -- examples: PCR00 (set device working range to appliance), PCR01 (set device working range to UPS)
POP  - Set Device Output Source Priority  -- examples: POP00 (set Utility > Solar > Battery), POP01 (set Solar > Utility > Battery), POP02 (set Solar > Battery > Utility)
POPLG  - Set Device Operation Logic  -- examples: POPLG00 (set Auto mode), POPLG01 (set Online mode), POPLG02 (set ECO mode)
POPM  - Set Device Output Mode (for 4000/5000)  -- examples: POPM01 (set unit 0 to 1 - parallel output), POPM10 (set unit 1 to 0 - single machine output), POPM02 (set unit 0 to 2 - phase 1 of 3), POPM13 (set unit 1 to 3 - phase 2 of 3), POPM24 (set unit 2 to 4 - phase 3 of 3)
[...output truncated...]
```

### List Output formats

```
$ powermon-cli --listFormats
Available output formats
HASS: hass: generates Home Assistant auto config and update mqtt messages
HASS_AUTODISCOVERY: hass_autodiscovery: generates Home Assistant auto config (only) mqtt messages
HASS_STATE: hass_state: generates Home Assistant state update mqtt messages (requires entities to exist or HassAutoDiscovery to have been run first)
HTMLTABLE: htmltable: generates html table of results
JSON: json: generates json representation of the results
RAW: raw: outputs the response as received from the device
SIMPLE: simple: generates a simple representation of the results, eg 'soc=89%'
TABLE: table: generates a table of the results (optionally formatted with line art boxes)
BMSRESPONSE: bmsresponse: generates the BMSResponse for a PI30 inverter
CACHE: cache: generates mqtt messages suited to populating the results cache
```

### Compare Protocols

```
$ powermon-cli --compareProtocols pi30,pi30max

=====================
PROTOCOL COMPARISON
=====================
pi30 has 45 commands
pi30max has 67 commands
Commands with the same definition in both protocols (36)
        ['PCP', 'F', 'PBFT', 'QMN', 'QBMS', 'POP', 'PBATMAXDISC', 'POPM', 'MNCHGC', 'DAT', 'PPVOKC', 'PBCV', 'PBT', 'PCVV', 'Q1', 'QMUCHGCR', 'PPCP', 'BTA', 'QPI', 'QVFW', 'PGR', 'MCHGC', 'PBDV', 'PSAVE', 'QOPM', 'PBATCD', 'PSDV', 'PE', 'QBOOT', 'PSPB', 'PF', 'PD', 'MUCHGC', 'POPLG', 'QGMN', 'QMCHGCR']
Commands in pi30max but not pi30 (23)
        {'PLEDT', 'PLEDB', 'QEY', 'QVFW3', 'QOPPT', 'PLEDM', 'PLEDC', 'QLM', 'VERFW', 'QPIGS2', 'QLD', 'QLY', 'QBEQI', 'QLT', 'QT', 'QET', 'PLEDE', 'QSID', 'QEM', 'QLED', 'QED', 'PLEDS', 'QCHPT'}
Commands in pi30 but not pi30max (1)
        {'QVFW2'}
Commands in both protocols with different config (8)
        ['QPIWS', 'QID', 'QDI', 'QPGS', 'QPIGS', 'QMOD', 'QFLAG', 'QPIRI']

QPIWS
|                        description|                                      Warning status inquiry|Warning status inquiry                                      |
|                          help_text|      -- queries any active warnings flags from the Inverter|Not Present                                                 |
|                        result_type|                                           ResultType.SINGLE|ResultType.SINGLE                                           |
|                              regex|                                                            |                                                            |
|                            aliases|                                                            |                                                            |
|                       command_type|                                                            |                                                            |
|                       command_code|                                                            |                                                            |
|                       command_data|                                                            |                                                            |
|                          construct|                                                            |                                                            |
|             construct_min_response|                                                           8|8                                                           |
|             test_responses (count)|                                                           1|2                                                           |
|        reading_definitions (count)|                                                           1|1                                                           |
|                     rd[0]: Warning|                                                     Matches|                                                            |

[...output truncated...]
```
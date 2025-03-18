Powermon-cli Usage
==================

So far there are several uses for the ``powermon-cli`` command

# list the available protocols

    * ``powermon-cli --listProtocols``

# List available commands in a given protocol

    * ``powermon-cli --listCommands PI30``

# List available output modules

    * ``powermon-cli --listOutputs``

# List available output formats

    * ``powermon-cli --listFormats``

# generating a config file starter from the answers of a series of questions

    * ``powermon-cli -g``

# compare two protocols (and optionally a single command in each protocol)

    * ``powermon-cli --compareProtocols pi30,pi30max``  (compare the pi30 and pi30max protocols)
    * ``powermon-cli --compareProtocols pi30,pi30max:QMOD``  (compare the QMOD command from the pi30 and pi30max protocols)

# scan for details of BLE devices (with options to show additional details) 

    * ``powermon-cli --bleScan --details --advData --getChars``


Command Options
---------------

.. code-block:: console
    :caption: powermon command options

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


List Protocols
---------------

.. code-block:: console
    :caption: list available protocols

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


List Commands in a protocol
----------------------------

.. code-block:: console
    :caption: list commands in PI30 protocol

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


List Output formats
--------------------

.. code-block:: console
    :caption: available output formats

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


Compare Protocols
-----------------

.. code-block:: console
    :caption: compare PI30 and PI30MAX protocols

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
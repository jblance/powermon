Powermon-cli Usage
==================

So far there are 3 uses for the ``powermon-cli`` command

* generating a config file starter from the answers of a series of questions

  * ``powermon-cli -g``

* compare two protocols (and optionally a single command in each protocol)

  * ``powermon-cli --compareProtocols pi30,pi30max``  (compare the pi30 and pi30max protocols)
  * ``powermon-cli --compareProtocols pi30,pi30max:QMOD``  (compare the QMOD command from the pi30 and pi30max protocols)

* scan for details of BLE devices (with options to show additional details) 

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
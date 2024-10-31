Powermon-cli Usage
==================

Command Options
---------------

.. code-block:: console
    :caption: powermon command options

    $ powermon-cli -h
    usage: powermon-cli [-h] [-v] [-g] [--bleScan] [--details] [--advData] [--getChars] [--address ADDRESS]

    Power Device Monitoring Utility CLI, version: 1.0.15-dev, python version: 3.11.7

    options:
    -h, --help            show this help message and exit
    -v, --version         Display the version
    -g, --generateConfigFile
                            Generate Config File
    --bleScan             Scan for BLE devices
    --details             Show extra BLE device data
    --advData             Include advertisement data in BLE Scan
    --getChars            Connect to BLE device(s) and list characteristics
    --address ADDRESS     Only scan for supplied mac address


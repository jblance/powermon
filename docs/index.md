# Powermon

---

Python package designed to get information from inverters and other solar inverters and power monitoring devices

Currently has support for:

* MPP-Solar and similar inverters, e.g.
    * PIP-4048MS
    * IPS-4000WM
    * Voltronic Axpert MKS 5KVA Off-grid Inverter-Chargers
    * LV5048
* JK BMS
* Victron VE Direct Devices, e.g. SmartShunt 500A
* Daly BMS
* Neey / Heltec active balancers

## Installation

powermon is packaged on pypi and can be installed via pip, i.e.: 

    pip install powermon

There are a number of optional dependancies that can be installed based on the components required [see extended instructions](usage/usage.md#installation)

## Usage

powermon requires a config file, and the simplest usage is: 

    powermon -C /path/to/configfile.yaml

see [full usage options](usage/usage.md#powermon-command)


   j4_config_file
   j5_tutorials
   j6_docker
   j7_development
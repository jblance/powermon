Powermon
========
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

Installation
------------

.. code-block:: console

   pip install powermon           # minimal install
   pip install powermon[api]      # include web api dependancies
   pip install powermon[ble]      # include web bluetooth dependancies
   pip install powermon[dev]      # include development dependancies
   pip install powermon[modbus]   # include modbus dependancies
   pip install powermon[systemd]  # include systemd dependancies

Contents
--------

.. toctree::
   :maxdepth: 3

   modules
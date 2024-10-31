Usage
=====

Standard usage
--------------

``powermon -C /path/to/configfile.yaml`` 

Note: Config file syntax is described in :doc:`config_file`

Command Options
---------------

.. code-block:: console
    :caption: powermon command options

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

List Available Protocols
------------------------

.. code-block:: console
    :caption: list protocols

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

List Available Commands for a Protocol
--------------------------------------

.. code-block:: console
    :caption: available commands for NEEY protocol

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


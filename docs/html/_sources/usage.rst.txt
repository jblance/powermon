Usage
=====
powermon usage ...

.. code-block:: console
    :caption: powermon command options

    $ powermon -h
    usage: powermon [-h] [-C [CONFIGFILE]] [--config CONFIG] [-V] [-v] [--listProtocols] [-1] [--force] [-D] [-I] [--adhoc ADHOC]

    Power Device Monitoring Utility, version: 1.0.10-dev, python version: 3.11.7

    options:
    -h, --help            show this help message and exit
    -C [CONFIGFILE], --configFile [CONFIGFILE]
                            Full location of config file
    --config CONFIG       Supply config items on the commandline in json format, 
                            eg '{"device": {"port":{"type":"test"}}, "commands": [{"command":"QPI"}]}'
    -V, --validate        Validate the configuration
    -v, --version         Display the version
    --listProtocols       Display the currently supported protocols
    -1, --once            Only loop through config once
    --force               Force commands to run even if wouldnt be triggered
                            (should only be used with --once)
    -D, --debug           Enable Debug and above (i.e. all) messages
    -I, --info            Enable Info and above level messages
    --adhoc ADHOC         Send adhoc command to mqtt adhoc command queue
                             - needs config file specified and populated

Standard usage is ``powermon -C /path/to/configfile.yaml`` 

Config File Syntax
==================
There are 5 sections in the config file:
- ``device`` [required]
- ``commands`` [required]
- ``mqttbroker`` [optional]
- ``api`` [optional]
- ``daemon`` [optional]

Config Section - device
-----------------------

.. code-block:: yaml
    :caption: device section example

    device:
        name: My Inverter          # user name for physical device
        id: 123456789              # unique id of the physical device (suggest serial number)
        model: 1012LV-MK           #
        manufacturer: MPP-Solar    #
        port:
            type: test             # must be one of test, usb, serial, ble
            protocol: PI30         # [defaults to PI30] the protocol must be defined for any type of port
                                   #  - valid protocols are listed in the protocols document
                                   # the options for each port type are shown in separate sections below

.. code-block:: yaml
    :caption: port - test

    port:
        type: test                # test port - returns one of the defined test_responses 
                                  #  in the protocol definition - used for testing protocols
        protocol: PI30
        response_number: 0        # [optional] - if defined uses the number test_response 
                                  #  from the protocol command definition (0 is first test_response)


.. code-block:: yaml
    :caption: port - usb

    port:
        type: usb                 # usb port - uses direct usb access to device 
                                  #  (as opposed to serial which needs a usb to serial converter)
        protocol: PI30
        path: /dev/hidrawX        # X can be a number to specify a particular path
                                  #   or a wildcard (eg ?) to check a range of paths 
        identifier: XX1234566     # [optional] if path uses a wildcard identifier
                                  #   must be what is returned by the protocol get_id command


.. code-block:: yaml
    :caption: port - serial

    port:
        type: serial              # serial port - typically uses a usb to serial converter to connect to the device
        protocol: PI30
        path: /dev/ttyUSBX        # X can be a number to specify a particular path
                                  #   or a wildcard to check a range of paths 
        baud: 2400                # [optional, defaults to 2400] baud rate of connection 
        identifier: XX1234566     # [optional] if path uses a wildcard, identifier 
                                  #   must be what is returned by the protocol get_id command


.. code-block:: yaml
    :caption: port - ble

    port:
        type: ble              # ble port - uses Bluetooth Low Energy to connect 
                               #  to device and get info via BLE characteristics 
        protocol: PI30
        mac: 00:00:00:00:00    # mac address of ble device
        victron_key: !ENV ${VICTRON_KEY}  # [optional] required for victron devices - see XXXX document


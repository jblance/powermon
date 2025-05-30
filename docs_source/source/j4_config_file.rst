Config File Syntax
==================
There are 6 sections in the config file:

* :ref:`devices` [required]
* :ref:`loop` [optional]
* :ref:`mqttbroker` [optional]
* :ref:`daemon` [optional]
* :ref:`api` [optional]
* :ref:`debuglevel` [optional]

Note: the ``powermon-cli`` has an option to generate a config file based on the answers to questions see :doc:`j2.2_usage.powermon.cli`


.. _devices:

``devices``
==========
The devices section is a list of one or more devices, each device has details about the device, the connection port, and the 'commands' that should be run

The port section is required, with at least the ``type`` defined
The commands section details the commands to be run against the device. This section requires a list of ``command``s with each command having optional additional information:

* type
* override
* trigger
* outputs

.. code-block:: yaml
    :caption: devices section example

    devices:
      - name: My Inverter       # [optional] user name for physical device
        serial_number: 1234589  # [optional] serial number of physical device
                              # must be what is returned by get_id command
                              # if port path is a wildcard
        model: 1012LV-MK        # [optional] but used for adjusting some protocols
                              # eg PI30 protocol with model MAX uses the MAX version of the protocol
        manufacturer: MPP-Solar # [optional]
        port:
          type: test          # must be one of test, usb, serial, ble
          protocol: PI30      # [defaults to PI30] the protocol must be defined for any type of port
                            #  - valid protocols are listed in the protocols document
                            # the options for each port type are shown in separate sections below
        commands:
        - command: QPIGS        # command to execute (from protocol)
          type: basic           # [optional] defaults to basic, valid 'basic', 'templated', 'cache_query'
          overide: {}           # [optional] 
          trigger:              # [optional] 'every', 'loops', 'at'
            every: 5
          outputs:
          - type: screen
            format: table
          - type: screen
            format:
              type: table

The port section is required and must be one of ``test``, ``usb``, ``serial``, ``ble``, each of which has different config items/requirements

.. code-block:: yaml
    :caption: port - test

    port:
      type: test          # test port - returns one of the defined test_responses 
                          #  in the protocol definition - used for testing protocols
      protocol: PI30
      response_number: 0  # [optional] - if defined uses the number test_response 
                          #  from the protocol command definition (0 is first test_response)


.. code-block:: yaml
    :caption: port - usb

    port:
      type: usb           # usb port - uses direct usb access to device 
                          #  (as opposed to serial which needs a usb to serial converter)
      protocol: PI30
      path: /dev/hidrawX  # X can be a number to specify a particular path
                          #   or a wildcard (eg ?) to check a range of paths 


.. code-block:: yaml
    :caption: port - serial

    port:
      type: serial        # serial port - typically uses a usb to serial converter to connect to the device
      protocol: PI30
      path: /dev/ttyUSBX  # X can be a number to specify a particular path
                          #   or a wildcard to check a range of paths 
      baud: 2400          # [optional, defaults to 2400] baud rate of connection 


.. code-block:: yaml
    :caption: port - ble

    port:
      type: ble            # ble port - uses Bluetooth Low Energy to connect 
                           #  to device and get info via BLE characteristics 
      protocol: PI30
      mac: 00:00:00:00:00  # mac address of ble device
      victron_key: !ENV ${VICTRON_KEY}  # [optional] required for victron devices - see XXXX document

.. _loop:

``loop``
==========

The loop directive can either be ``once`` or a number. 
``once`` is mostly for testing and will run through the commands once and then exit, 
a number will define the number of seconds to pause at the end of each loop.
If the entry cannot be interpreted as a number then it will default to ``once``

Note: the effect of ``once`` can be forced on the command line by adding ``-1`` or ``--once`` to the ``powermon`` command

.. code-block:: yaml
    :caption: loop section example - will run through the commands once and then exit

    loop: once

.. code-block:: yaml
    :caption: loop section example - will add 5 sec delay to end of each loop

    loop: 5


.. _mqttbroker:

``mqttbroker``
==============

This section details the mqttbroker connection information

.. code-block:: yaml
    :caption: mqttbroker section example

    mqttbroker:
      name: 192.168.86.222
      port: 1833
      username:
      password:
      adhoc_topic: powermon/adhoc_commands
      adhoc_result_topic: powermon/adhoc_results


.. _daemon:

``daemon``
==========

This section configures the daemon settings

.. code-block:: yaml
    :caption: daemon section example

    daemon:
      type: systemd     # either 'systemd' or 'initd'
      keepalive: 100    # seconds between keepalive pings


.. _api:

``api``
==========


.. _debuglevel:

``debuglevel``
==============


***********************************************************
JKSERIAL - JK TTL Communications v2.5 - ``0x4E57`` | ``NW``
***********************************************************

Document Details
----------------

Source: http://www.jk-bms.com/en/Upload/2023-12-05/1702131628.pdf

Implemented in protocol: ``JKSERIAL``

Physical Interface
-------------------

This protocol defines the communication protocol between the monitoring platform and the battery terminal, as well as the message format, 
transmission mode and communication mode, etc.

Communication using 2G GPRS in TCP transmission, 4G in GAT1, Socket interface mode,
RS232TTL serial port, content custom communication format, baud rate 115200.

During the communication process, the device has active reporting frame and passive response frame. Please refer to the communication data
format for details. The interval of each packet number is at least 100MS, and the longest reply packet is not more than 5S. Timed broadcast. If
dormant, the control terminal will send the activation information, activate the BMS, and then communicate.

Frame Structure
---------------

Example: ``'NW\x00\x13\x00\x00\x00\x00\x06\x03\x00\x00\x00\x00\x00\x00h\x00\x00\x01)'``

.. csv-table:: Frame Structure
   :header: no, length, byte description, description
   :widths: auto
   :align: left

    1, 2, start bytes, ``0x4E57`` or ``NW``
    2, 2, length, ``0x0013`` all data bytes except the first two characters including the checksum and the length field itself
    3, 4, bms terminal no, ``0x00000000``
    4, 1, command word, ``0x06`` read all the data - see Command Word section5
    5, 1, frame source, "``0x03`` 0: BMS, 1: Bluetooth, 2: GPS, 3: PC"
    6, 1, transport type, "``0x00`` 0: request frame, 1: reply frame, 2: BMS active reporting"
    7, n, data, ``0x00`` not used for 'read all data' command
    8, 4, record number, "``0x00000000`` The high 1 byte is the random code meaningless (reserved for encryption), the low 3 bytes is the record sequence number"
    9, 1, end byte, ``0x68`` or ``h``
    10, 4, checksum, "``0x000001)`` high 2 bytes not yet enabled, low 2 bytes crc cumulative check"


Command Word
------------

- ``0x01`` - Activate - Activate the BMS (when dormant) before proceeding to any other action
- ``0x02`` - Write - Write / configure BMS parameter(s)
- ``0x03`` - Read - Read BMS parameter
- ``0x05`` - Pair - Pair with the BMS
- ``0x06`` - Read All Data - Read all BMS data at once

Transport Type
--------------

0 for request frame, 1 for reply frame. 2 is for active reporting.
As long as 5-Bluetooth,2-GPS,3-PC PC and 4-BMS are initiated first, the reply will use 1.

crc calc
-------------

.. code-block:: python
    :caption: crc calc - sum all data

    crc = 0
    for b in byte_data:
        crc += b
    crc_low = crc & 0xFF
    crc_high = (crc >> 8) & 0xFF


BMS Data
========
.. csv-table:: BMS Data Definitions
   :header: Use, Code, Name, "Byte Count", Description
   :widths: auto
   :align: left

   R, ``0x79``, Single Battery Voltage, 3*n, "the first byte is the battery number, the second is data length, then each 3 bytes is battery number, and 2 bytes of voltage in mV"
   R, ``0x80``, Power tube temperature, 2, "0 -- 140 (-40 to 100 °C) parts over 100 are negative temperatures, such as 10, 1 is negative 1 °C (100 Benchmark)"
   R, ``0x81``, Battery box temperature, 2, "0 -- 140 (-40 to 100 °C) parts over 100 are negative temperatures, such as 10, 1 is negative 1 °C (100 Benchmark)"
   R, ``0x82``, Battery temperature, 2, "0 -- 140 (-40 to 100 °C) parts over 100 are negative temperatures, such as 10, 1 is negative 1 °C (100 Benchmark)"
   R, ``0x83``, Total battery voltage, 2, "0.01V, eg 3500 * 0.01 = 35.00v The minimum unit is 10 mV"
   

...#TODO: finish ...

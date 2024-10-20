####
JKXX
####

*******************************************
Jiabaida Software Board General Protocol V4
*******************************************

Document Details
----------------

Source: https://cdn.shopifycdn.net/s/files/1/0606/5199/5298/files/JDB_RS485-RS232-UART-Bluetooth-Communication_Protocol.pdf?v=1682577935

Implemented in protocol:

Physical Interface
-------------------

This protocol supports RS485/RS232/UART interface of Jiabaida software board general protocol, consistent with the host computer protocol, The baud rate is 9600BPS or other customer customized rates

Frame Structure
---------------

=======  ==========  ================  =========================================
byte no  example     byte description  value - description
=======  ==========  ================  =========================================
0        ``0xDD``    start byte        - ``0xDD``
1        ``0xA5``    state             - ``0xA5`` - read
                                       - ``0x5A`` - write
2        ``0x03``    command           - ``0x03`` - basic information and status
                                       - ``0x04`` battery cell voltage
                                       - ``0x05`` BMS version
3        ``0x00``    data length
4-?                  data
-3:-2    ``0xfffd``  crc
-1       ``0x77``    end byte          - ``0x77``
=======  ==========  ================  =========================================


crc calc
-------------

sum of command code, length, data bytes, inverted + 1

.. code-block:: python
    :caption: crc calc example

    >>> # dd a5 03 00 ff fd 77 
    >>> hex((0xffff ^ sum(b'\x03\x00')) + 1)
    >>> '0xfffd'


Command Details - ``0x03`` Read Basic Information and Status
------------------------------------------------------------

Command: ``DD A5 03 00 FF FD 77``

Response: ``DD 03 00 1B 17 00 00 00 02 D0 03 E8 00 00 20 78 00 00 00 00 00 00 10 48 03 0F 02 0B 76 0B 82 FB FF 77``

.. code-block::
    :caption: response decode

    0xDD    start byte
    0x03    command
    0x00    status (00 is correct)
    0x1B    data length  1B=27
    0x1700  total voltage (10mV)        0x1700=5888 -> 58.88V
    0x0000  current (10mA)              0
    0x02D0  remaining capacity (10mAh)  0x02D0=720  -> 7.2Ah
    0x03E8  nominal capacity (10mAh)    0x03E8=1000 -> 10Ah
    0x0000  cycles                      0
    0x2078  production date             0x2078&0x1f=24, 0x2078>>5&1f=3, 0x2078>>9&0x1f=16 -> 24 Mar 2016
    0x0000  equilibrium                 (by bit) 1-16 cells, balanced 0=off, 1=on
    0x0000  equilibrium                 (by bit) 17-32 cells
    0x0000  protection status           (by bit) 0=unprotected, 1=protected
    0x10    software version            0x10 = version 1.0
    0x48    remaining soc               0x48 = 72%
    0x03    fet control                 0x03=0b11 -> bit0 is charge, bit1 is discharge 0=off 1=on
    0x0F    number of cells             0x0F = 15
    0x02    number of temp sensors      0x02 = 2
    0x0B76  temp sensor 1               0x0B76=2934 -> 2934-2731=203=20.3C
    0x0B82  temp sensor 2               0x0B82=2946 -> 2946-2731=215=21.5C
    0xFBFF  crc                         crc calc on bytes: 00 1B 17 00 00 00 02 D0 03 E8 00 00 20 78 00 00 00 00 00 00 10 48 03 0F 02 0B 76 0B 82
    0x77    end byte
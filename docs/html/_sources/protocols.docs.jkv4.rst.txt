Jiabaida Software Board General Protocol V4
===========================================

Document Details
----------------

Source: https://cdn.shopifycdn.net/s/files/1/0606/5199/5298/files/JDB_RS485-RS232-UART-Bluetooth-Communication_Protocol.pdf?v=1682577935
Implemented in protocol:

Physical Interface
-------------------

This protocol supports RS485/RS232/UART interface of Jiabaida software board general protocol, consistent with the host computer protocol, The baud rate is 9600BPS or other customer customized rates

Frame Structure
---------------

=======  ================  =======================================
byte no  byte description  value - description
=======  ================  =======================================
0        start byte        ``0xDD``
1        state             ``0xA5`` - read
                           ``0x5A`` - write
2        command           ``0x03`` - basic information and status
                           ``0x04`` battery cell voltage
                           ``0x05`` BMS version
3        data length
4-?      data
-3--2    crc
-1       end byte          ``0x77``
=======  ================  =======================================


==========  ============  ===================================  ===================  ============  ============  =========
Start Byte  Status Byte   Command Code                         Length               Data Content  Calibration   Stop Byte
==========  ============  ===================================  ===================  ============  ============  =========
0xDD        - 0xA5 read   - 0x03 basic information and status  length of data only  cc            see crc calc  0x77
            - 0x5A write  - 0x04 battery cell voltage           
                          - 0x05 BMS version                    
==========  ============  ===================================  ===================  ============  ============  =========


crc calc
-------------
sum of command code, length, data bytes, inverted + 1
eg for dd a5 03 00 ff fd 77 cmd
hex((0xffff ^ sum(b'\x03\x00')) + 1)
'0xfffd'
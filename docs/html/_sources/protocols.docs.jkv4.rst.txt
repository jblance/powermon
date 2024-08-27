General Protocol V4
===================

Physical Interface
-------------------

The protocol supports RS485 / RS232 / UART interface general protocol, consistent with the host computer protocol, Baud rate is 9600 BPS or other customized rate.

Frame Structure
---------------

=========  ============  ===================================  ===================  ============  ============  ========
Start Bit  Status Bit    Command Code                         Length               Data Content  Calibration   Stop Bit
=========  ============  ===================================  ===================  ============  ============  ========
0xDD       - 0xA5 read   - 0x03 basic information and status  length of data only  cc            see crc calc  0x77
           - 0x5A write  - 0x04 voltage of cell block         , 0 is to skip data
                         - 0x05 BMS version                   content
=========  ============  ===================================  ===================  ============  ============  ========


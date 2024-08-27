General Protocol V4
===================

Physical Interface
-------------------

The protocol supports RS485 / RS232 / UART interface general protocol, consistent with the host computer protocol, Baud rate is 9600 BPS or other customized rate.

Frame Structure
---------------

=========  ==========  ============  ======  ============  ===========  ========
Start Bit  Status Bit  Command Code  Length  Data Content  Calibration  Stop Bit
=========  ==========  ============  ======  ============  ===========  ========
0xDD       0xA5 read   xx            xx      cc            dd           0x77
           0x5A write
=========  ==========  ============  ======  ============  ===========  ========

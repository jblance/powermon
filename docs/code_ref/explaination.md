# Application Logic

powermon structure is:

* `powermon.py` is the main entry point for the code, the settings come from a yaml configuration file (spcified with `-C`)
* the config file has several sections:
    * devices: this is the main section and contains one or more named devices, each device has:
        * details about the device (name, manufacturer etc)
        * port details (details of the physical connection to the device - including what protocol to use to communicate)
        * actions: one or more actions to be performed (eg commands to run against the device) 

```yaml title='example config file'
devices:
  - name: Device 1
    serial_number: A123456789
    model: 8048MAX
    manufacturer: MPP-Solar
    port:
      type: serial
      path: /dev/ttyUSB0
      protocol: PI30MAX
    actions:
      - command: QPI
        outputs:
        - type: screen
          format: 
            type: table
```
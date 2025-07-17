# Troubleshooting

## USB Permission denied error

When you use Powermon to access a USB device on Linux, you may run into
Permission denied error. It’s because by default, the device nodes are
owned by ``root``. To run Powermon as a non-root user, you have to
change the permissions of the device nodes with ``udev`` rules .

First, run Powermon as root to confirm that you can talk to your
inverter or BMS:

``sudo powermon -C inverter-conf.yaml``

Where ``inverter-conf.yaml`` is the path to your YAML config.

After running the above command, you should see the values from your
device, according to the settings in the YAML config file. If not, make
sure that the cable is plugged in on both ends and that you chose the
right device.

### udev rules - basic

For everyday monitoring, don’t run it as root. Instead, change the
permissions with ``udev`` rules:

1. Create file ``60-powermon-usb.rules`` in the ``etc/udev/rules.d``
   directory if it doesn’t exist:

   ``sudo touch /etc/udev/rules.d/60-powermon-usb.rules``

2. Open the file with a text editor (for example ``nano``):

   ``sudo nano /etc/udev/rules.d/60-powermon-usb.rules``

3. Paste the following lines:

   - for devices connected through ``hidraw``:
   
   ``KERNEL=="hidraw[0-9]*", SUBSYSTEM=="hidraw", MODE="0666"``

   - for devices connected through ``ttyUSB``:
   
   ``KERNEL=="ttyUSB[0-9]*", MODE="0666"``

4. Save the file.
5. Reload the udev rules:

   1. ``sudo udevadm control --reload-rules``
   2. ``sudo udevadm trigger``

6. Run Powermon as a regular user to confirm it’s working:

   1. ``powermon -C inverter-conf.yaml``

This rule makes any ``hidraw`` and ``ttyUSB`` devices to be readable and 
writable by any user on the system. 

### udev rules - advanced

Such broad permissions are not always desirable. You can use more restrictive 
permissions by targeting specific vendor and product IDs:

1. Find the vendor and product IDs:

   1. ``lsusb``
   2. If you see multiple devices, unplug your cable, run ``lsusb``
      again, and compare which devices are missing. Note the device IDs
      and name.
   3. List the attributes of the specific device:

      1. ``udevadm info --attribute-walk --path=$(udevadm info --query=path --name=/dev/ttyUSB0)``
         - replace ``/dev/ttyUSB0`` with your device.
      2. look for ``ATTRS{idProduct}==`` and ``ATTRS{idVendor}==`` that
         match the IDs from your previous ``lsusb`` command.
      3. In our case we found ``ATTRS{idProduct}=="7523"`` and
         ``ATTRS{idVendor}=="1a86"``.

2. Create file ``60-powermon-usb.rules`` in the ``etc/udev/rules.d``
   directory if it doesn’t exist:

   - ``sudo touch /etc/udev/rules.d/60-powermon-usb.rules``

3. Open the file with a text editor (for example ``nano``):

   - ``sudo nano /etc/udev/rules.d/60-powermon-usb.rules``

4. Edit the file. If there are existing rules for the matching device,
   remove them.

   -  In our case, we’re editing ``dev/ttyUSB0`` rules
   -  We replace the existing line
      ``KERNEL=="ttyUSB[0-9]*", MODE="0666"`` with
      ``KERNEL=="ttyUSB[0-9]*", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0660", TAG+="uaccess"``
   -  By providing the exact vendor and product ID, we limit the rule to
      a specific device.
   -  Note the ``MODE`` is now ``0660`` (zero at the end).
   -  ``TAG+="uaccess"`` makes the device usable to logged-in users.
   -  In the future, if you replace the cable, you might need to change
      the vendor and product ID.

5. Save the file.
6. Reload the udev rules:

   1. ``sudo udevadm control --reload-rules``
   2. ``sudo udevadm trigger``

7. Run Powermon as a regular user to confirm it’s working:

   1. ``powermon -C inverter-conf.yaml``

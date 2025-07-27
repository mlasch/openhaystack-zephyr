##############################
 OpenHaystack Zephyr firmware
##############################

This project implements firmware with an `OpenHaystack
<https://github.com/seemoo-lab/openhaystack>`_ application based on the real-time operating system
`Zephyr <https://www.zephyrproject.org/>`_.

OpenHaystack is a framework for tracking personal Bluetooth devices via Apple's massive `Find My
<https://developer.apple.com/find-my/>`_ network. Thanks to this firmware based on Zephyr, you can
create your own tracking tags with one of the many Bluetooth Low Energy devices that Zephyr
supports.

After flashing the firmware to your device, it sends out Bluetooth Low Energy advertisements that
will be visible in Apple's Find My network using the OpenHaystack application in macOS.

************
 Disclaimer
************

The firmware is just a proof-of-concept and currently only implements advertising a single static
key. This means that devices running this firmware are trackable by other devices in proximity.

There is also no power management implemented yet. So if you're running this firmware on a
battery-powered device, it won't be as energy-efficient as possible.

**************
 Requirements
**************

-  A Bluetooth Low Energy device, supported by Zephyr
-  A `Zephyr development environment
   <https://docs.zephyrproject.org/latest/getting_started/index.html>`_
-  OpenHaystack's macOS application to view the location of your device

****************
 Initialization
****************

The first step is to initialize a workspace folder (for instance ``zephyr-workspace``) where the
application and all Zephyr modules will be cloned. You can do that by running:

.. code:: shell

   # Initialize Zephyr workspace folder for the application (main branch)
   west init -m https://github.com/mlasch/openhaystack-zephyr --mr main zephyr-workspace
   # Update Zephyr modules
   cd zephyr-workspace
   west update
   cd openhaystack-zephyr

*******
 Build
*******

To build the firmware, run:

.. code:: shell

   west build -p auto -b $BOARD -s app

Replace ``$BOARD`` by your target board.

Once you have built the application, the firmware image is available in ``build/zephyr``.

******************
 Use your own key
******************

You need to specify a public key in the firmware image. The firmware loads the key from the
`airtag/public_key` settings entry.

One way to get a valid public key is to sniff an Apple AirTag BLE advertisement.

The `gen_settings_nvs.py` script can be used to generate a pre-loaded settings hex file.

********************************
 Using OpenHaystack as a module
********************************

The base code is written as a Zephyr module, in the directory `modules/openhaystack
<https://github.com/koenvervloesem/openhaystack-zephyr/tree/main/modules/openhaystack>`_. You can
reuse this in your own Zephyr applications. For examples of how you do this, take a look at:

-  the application of this repository in the directory `app
   <https://github.com/koenvervloesem/openhaystack-zephyr/tree/main/app>`_
-  the `Send My Sensor <https://github.com/koenvervloesem/send-my-sensor>`_ project, which uses the
   OpenHaystack module to upload sensor data via Apple's Find My network.

***********
 Debugging
***********

A sample debug configuration to read logs from the USB UART is also provided. You can apply it by
running:

.. code:: shell

   west build -p auto -b $BOARD -s app -- -DOVERLAY_CONFIG=debug-usb-uart.conf

This only works with boards that support this, such as Nordic Semiconductor's nRF52840 Dongle.

For the UART logs: run ``ls /dev/tty*`` (Linux) or ``ls /dev/cu.*`` (macOS) in a terminal window,
connect your board and run the command again to check which port appears. On Linux, this will
probably be /dev/ttyACM0. Then run ``screen /dev/ttyACM0 115200`` to connect to port /dev/ttyACM0
with a speed of 115200 bits per second.

***************************************************
 Learn more about Bluetooth Low Energy development
***************************************************

If you want to learn more about Bluetooth Low Energy development, read my book `Develop your own
Bluetooth Low Energy Applications for Raspberry Pi, ESP32 and nRF52 with Python, Arduino and Zephyr
<https://koen.vervloesem.eu/books/develop-your-own-bluetooth-low-energy-applications/>`_ and the
accompanying GitHub repository `koenvervloesem/bluetooth-low-energy-applications
<https://github.com/koenvervloesem/bluetooth-low-energy-applications>`_.

*****************
 Acknowledgments
*****************

This project is inspired by and has used code from:

-  this repo is based on the `OpenHaystack Zephyr firmware
   <https://github.com/koenvervloesem/openhaystack-zephyr>`_
-  the original `OpenHaystack firmware for ESP32
   <https://github.com/seemoo-lab/openhaystack/tree/main/Firmware/ESP32>`_
-  the original `OpenHaystack firmware for nRF51822
   <https://github.com/seemoo-lab/openhaystack/tree/main/Firmware/Microbit_v1>`_
-  Antonio Calatrava's alternative `OpenHaystack firmware using Nordic Semiconductor's Softdevice
   <https://github.com/acalatrava/openhaystack-firmware>`_
-  the `Zephyr Example Application <https://github.com/zephyrproject-rtos/example-application>`_ for
   the project structure and GitHub Actions workflow

*********
 License
*********

This project is provided by `Koen Vervloesem <http://koen.vervloesem.eu>`_ as open source software
with the MIT license. See the `LICENSE file <LICENSE>`_ for more information.

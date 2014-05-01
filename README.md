sensortag2mqtt
==============

TI BLE Sensortag data to mqtt
This python script takes data from a Texas instruments sensortag and publishes it to MQTT.

The script takes the below work from Michael Saunby and extends it to incorporate output to MQTT,

It currently takes 2 input forms, a mac address of the sensortag (see below) and a config file,
the config file allows the mqtt broker details to be stored, a sample file exists to work from.


Original work to output temperature data to console:

 Michael Saunby. April 2013

 Read temperature from the TMP006 sensor in the TI SensorTag
 It's a BLE (Bluetooth low energy) device so using gatttool to
 read and write values.

 Usage.
 sensortag_temp2mqtt.py BLUETOOTH_ADR

 To find the address of your SensorTag run 'sudo hcitool lescan'
 You'll need to press the side button to enable discovery.

 Notes.
 pexpect uses regular expression so characters that have special meaning
 in regular expressions, e.g. [ and ] must be escaped with a backslash.




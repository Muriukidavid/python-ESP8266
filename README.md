# ESP8266 AT API

This is a python API for ESP8266 chip AT command protocol 

It makes it easy to connect to an AP, get ESP8266 module connection information, connect to a remote TCP host and upload/get data.

For a giude on how to use it, check out the test.py file

## Available functions 👨‍💻️

	- test
	- reset
	- sendString
	- sendCommand
	- getResponse
	- connect
	- ThingspeakConnect
	- SendValues
	- wifi_mode: setter

## Class object properties

	- version: The version information of the AT protocol, the SDK and the firmware Binary
	- wifi_status: Whether connected to an Access Point or disconnected
	- connected_ap: The ssid of the Access point it is connected to
	- ap_address: MAC address of the Access Point it is connected to
	- wifi_mode : whether in Station/client or Access Point mode
	- local_ip : the IP address allocated to the module by the access point
	
Thi is a work in progress 🐍️

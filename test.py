#!/usr/bin/python3.6
import time
import random
from esp8266 import ESP8266

tty = "/dev/ttyUSB1"
baud = 115200

ssid = "WAGWAN"
password = "_estVmbUl45oi2jas80)19#@t^J"


dongle = ESP8266(tty, baud)

print("ESP8266 version:")
print(dongle.version)
print()

print("MAC address: ", dongle.mac_address)
dongle.wifi_mode = 1 # set Station/client mode
print(dongle.wifi_mode)#check mode

if dongle.wifi_status=="NOT connect to an AP":
	dongle.connect(ssid, password, 10)# connect to your Access Point
#print(dongle.wifi_status)# check status
if dongle.wifi_status=="connected to an AP and its IP is obtained":
	print("AP: ", dongle.connected_ap, ", address: ", dongle.ap_address)
	print("Local IP: ", dongle.local_ip)

# open a TCCP/IP connection to thingspeak.com
URL = "184.106.153.149";
port = 80
key = ""

#sendValues(URL="184.106.153.149", port=80, values=40, key = "WJNNIN8AAMFO1UZX")
for i in range(1,20):
	value = random.randint(20,40)
	print("Value: ", value)
	if(dongle.sendValues(URL, port, value, key)):
		print("Data sent")
	else:
		print("Failed sending")
	#wait 10 minutes
	time.sleep(10*60)
#Sequence commands for sending values manually in a serial console:	
#AT+CIPMUX=1
#AT+CIPSTART=4,"TCP","184.106.153.149",80
#AT+CIPSEND=4,44	
#GET /update?key=WJNNIN8AAMFO1UZX&field1=12

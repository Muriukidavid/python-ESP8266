#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import serial
import time

CIPSEND_BUFFER_SIZE = 2048

class ESP8266(object):    
	def __init__(self,port, speed):
		"""
		Initialize the ESP8266 object
		:param port: A serial port device
        :type port: A string, path to device in Unix based systems
        :param speed: A baudrate value
        :type speed: an integer value
		"""
		self.serial_port = serial.Serial(str(port), speed, timeout=1)
		if not self.serial_port.isOpen():
			self.serial_port.open()
		if self.test()=="unresponsive":
			if(self.reset()):
				if self.test()=="unresponsive":
					print("ESP8266 module unresponsive on port:"+ str(port) +" at speed:"+ str(speed))
					exit(-1)
			else:
				print("Failed to reset ESP8266")
			
	def __enter__(self):
		return self
		
	def __exit__(self,exc_type, exc_val, exc_tb):
		if self.autocleanup:
			self.close()
    
	def close(self):
		if(self.serial_port):
			self.serial_port.close()

	def sendString(self,_str):
		""" Sends a string to the ESP8266 module """
		self.serial_port.flushInput()
		self.serial_port.write(_str.encode('utf-8'))
		self.serial_port.readline() # pre-read the command echo
        
	def sendCommand(self,cmd, expected, timeout=4):
		""" 
		Sends a command to the ESP8266 module and returns the response 
		"""
		if(cmd=="AT"):
			return self.test()
		else:
			self.sendString("AT+"+cmd+"\r\n")
			return self.getResponse(expected+"\r\n", timeout)
   
	def getResponse(self,expected, timeout=4):
		""" 
		Returns the response from the ESP8266 module after sending a command 
		:param expected: The expected tailstring
        :type ssid: A string
        :param timeout: Time in seconds to wait for response before giving up
        :type password: integer
		"""
		lines = []
		timer = 0;
		while True:
			line = self.serial_port.readline().decode("utf-8", errors="ignore")
			if line:
				if expected in line:
					lines.append(line.strip())
					#print("\nResponse Tries: ", timer, "\n")
					return lines
				elif "ERROR" in line:
					return ["ERROR: ", line];
				elif "FAIL" in line:
					lines.append(line.strip())
					return lines
				lines.append(line.strip())
			else:#DONE: deal with timeouts better
				timer +=1;
				time.sleep(1)#wait for 1 second
				if(timer>timeout):
					print('TIMEOUT: response so far:')
					print(lines)
					return lines
	
	def test(self):
		""" Returns the state of the ESP8266 module ["ready" or "unresponsive"]  """
		self.sendString("AT\r\n")
		result = self.getResponse("OK\r\n")
		if(str(result[-1]).strip() == "OK"):
			return "ready"
		else:
			return "unresponsive";
	        
	def reset(self):
		result = self.sendCommand("RST", "ready") 
		if(str(result[-1]).strip() == "ready"):
			return True
		else:
			return False
			
	@property		
	def version(self):
		""" Prints the firmware SDK and versions as well as compile time """
		result = self.sendCommand("GMR", "OK")
		if(str(result[-1]).strip() == "OK"):
			result.pop(-1)
			return "\n".join(result)
			#for element in result:
			#	print(element)
		else:# TODO: deal with errors better
			print("Error getting version information")
	
	@property
	def wifi_status(self):
		""" Gets the connection status of the module """
		status = {
			2: "connected to an AP and its IP is obtained",
			3: "created a TCP or UDP transmission",
			4: "TCP or UDP transmission of ESP8266 Station is disconnected",
			5: "NOT connect to an AP",
		}
		result = self.sendCommand("CIPSTATUS", "OK")
		if result[-1]=="OK":
			pieces = result[0].split(":")
			return status[int(pieces[1])]
		else:
			print("Could not get status")
			
	@property
	def connected_ap(self):
		"""
		Returns the ssid of the access point to which the ESP8266 Station is already connected
		"""
		if(self.wifi_status=="NOT connect to an AP"):
			#print(self.wifi_status)
			print("NO AP connection")
		else:
			result = self.sendCommand("CWJAP?", "OK")
			#print(result)
			if result[-1] == "OK":
				result.pop(-1)
				return str(result[0].split(":")[1].split(",")[0]).strip("\"")
				
	@property
	def ap_address(self):
		"""
		Returns the address of access point to which the ESP8266 Station is already connected
		"""
		if(self.wifi_status=="NOT connect to an AP"):
			#print(self.wifi_status)
			print("NO AP connection")
		else:
			result = self.sendCommand("CWJAP?", "OK")
			#print(result)
			if result[-1] == "OK":
				return str(result[0].split("\"")[3])
			
	@property
	def wifi_mode(self):
		""" Returns the current WiFi mode """
		modes = {
			1: "Station/Client mode",
			2: "SoftAP/Hotspot mode",
			3: "SoftAP+Station mode",
		}
		result = self.sendCommand("CWMODE?", "OK")
		if result[-1]=="OK":
			#print(result)
			pieces = result[0].split(":")
			return modes.get(int(pieces[1]))
	
	@wifi_mode.setter	
	def wifi_mode(self,mode):
		""" Sets WiFi mode: Station, AP or both """
		modes = {
			1: "Station/Client mode",
			2: "SoftAP/Hotspot mode",
			3: "SoftAP+Station mode",
		}
		result = self.sendCommand("CWMODE="+str(mode),"OK")
		if not (result[-1]=="OK"):
			print("Failed to set wifi mode")
	
	@property		
	def local_ip(self):
		"""
		Returns the IP address of the module if connected
		"""
		if self.wifi_status=="connected to an AP and its IP is obtained":
			result = self.sendCommand("CIFSR", "OK")
			# +CIFSR:STAIP,<Station IP address>
			#+CIFSR:STAMAC,<Station MAC address>
			#OK
			#print(result)
			if result[-1] == "OK":
				pieces = result[0].split(",")
				return pieces[1].strip("\"")
	@property		
	def mac_address(self):
		"""
		Returns the MAC address of the ESP8266 module
		"""
		result = self.sendCommand("CIPSTAMAC?", "OK")
		#print(result)
		if result[-1] == "OK":
			return result[0].split("\"")[1]
			
		else:
			print("Failed to get MAC address")
			
		
	def connect(self,ssid, password, timeout):
		""" 
		connects to a WiFi Network and returns the IP address
		:param ssid: Name of the WIFI AP
        :type ssid: A string
        :param password: The password for the AP
        :type password: A string
        :param timeout: The time to wait for a response before 
        :type timeout: int
		"""
		if(self.wifi_status=="NOT connect to an AP"):# Disconnected, need to connect
			self.wifi_mode = 1# set to client
			result = self.sendCommand("CWJAP=\""+ssid+"\",\""+password+"\"", "OK") 
			if result[-1]=="OK":
				if "WIFI GOT IP" in result[-3]:
					#get the IP address
					print("connected, IP: ", self.local_ip)
			elif result[-1]=="FAIL":
				print("Failed to connect to "+ssid)
			else:
				print("Something went horribly wrong")
		else:
			print("connected, IP: ", self.local_ip)
			
	def thingspeakConnect(self, URL, port):
		"""
		Starts a TCP onnection to thingspeak.com
		:param URL: The thingspeak.com API IP address
		:type URL: String
		:param port: The connection port, 80 for TCP
		:type port: int
		"""
		#AT+CIPSTART=<type>,<remote IP>,<remote port>[,<TCP keep alive>]
		#AT+CIPSTART=4,"TCP","184.106.153.149",80
		result = self.sendCommand("CIPMUX=1", "OK")
		#print results
		if result[-1] == "OK":
			result = self.sendCommand("CIPSTART=4,\"TCP\",\""+str(URL)+"\","+str(port), "OK",4)
			#print(result)
			if result[-1]=="OK":
				time.sleep(1)
				return True
			else:
				return False
		else:
			print("Failed to connect to thingspeak")
		
	def sendValues(self, URL, port, values, key):
		"""
		Updates a thingspeak channel with values using a write API key
		:param URL: URL for thingspeak API, actually an IP address works better
        :type URL: A string
        :param port: The connection port, 80 for TCP
        :type port: int
        :param values: The values to be updated in the fields, follows order: field1, field2, e.t.c
        :type values: list
        :param key: The thingspeak write API key
        :type key: A string
		"""
		#construct an update query string
		query = "GET /update?key="+str(key)+"&field1="+str(values)+"\r\n"
		self.thingspeakConnect(URL, port)
		self.sendString("AT+CIPSEND=4,44"+"\r\n")
		resp = self.getResponse(">", 3)
		if resp[-1] == ">":
			self.sendString(query)
			#Wait for acknowledgement data was sent
			result = self.getResponse("SEND OK",5)
			#wait for session to close???
			res = self.getResponse("CLOSED",15);
			if result[-1]=="SEND OK":
				#close the connection
				result = self.sendCommand("CIPCLOSE", "MUX=1", 5)
				return True
			else:
				return False
		

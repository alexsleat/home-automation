#!/usr/bin/python

#
# Code based on https://gist.github.com/mr-pj/75297864abef5c8f2d5c134be2656023
#

from pydhcplib.dhcp_network import *
import requests
from datetime import timedelta, datetime
from qhue import Bridge
import settings as s

FAIRY_LAST = datetime.now()
ANDREX_LAST = datetime.now()

def toggle_qhue():
	b = Bridge(s.hue.bridge_up, s.hue.app_key)

	#lights = b.lights()
	val = b.groups[1]()['state']['any_on']
	if val == True:
		b.lights[2].state(on=False)
		b.lights[3].state(on=False)
	else:
		b.lights[2].state(on=True)
		b.lights[3].state(on=True)
		b.lights[2].state(bri=128)
		b.lights[3].state(bri=128)

def fairy_do_something():
	global FAIRY_LAST
	if FAIRY_LAST < datetime.now() + timedelta(seconds = -5):  # 5 second debounce
		FAIRY_LAST = datetime.now()
		print("Fairy has been pressed")
		## Using IFTT:
		# requests.post("https://maker.ifttt.com/trigger/fairy_dash_button/with/key/" + s.ifttt.key)
		## Using phue library:
		toggle_qhue()
	
def andrex_do_something():
	global ANDREX_LAST
	if ANDREX_LAST < datetime.now() + timedelta(seconds = -5):  # 5 second debounce
		ANDREX_LAST = datetime.now()
		print("Andrex has been pressed")
		requests.post("https://maker.ifttt.com/trigger/andrex_dash_button/with/key/" s.ifttt.key)

netopt = {'client_listen_port':"68", 'server_listen_port':"67", 'listen_address':"0.0.0.0"}

class Server(DhcpServer):
	def __init__(self, options, dashbuttons):
		DhcpServer.__init__(self, options["listen_address"],
								options["client_listen_port"],
								options["server_listen_port"])
		self.dashbuttons = dashbuttons

	def HandleDhcpRequest(self, packet):
		mac = self.hwaddr_to_str(packet.GetHardwareAddress())
		self.dashbuttons.press(mac)


	def hwaddr_to_str(self, hwaddr):
		result = []
		hexsym = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
		for iterator in range(6) :
			result += [str(hexsym[hwaddr[iterator]/16]+hexsym[hwaddr[iterator]%16])]
		return ':'.join(result)

class DashButtons():
	def __init__(self):
		self.buttons = {}

	def register(self, mac, function):
		self.buttons[mac] = function

	def press(self, mac):
		if mac in self.buttons:
			self.buttons[mac]()
			return True
		return False

dashbuttons = DashButtons()
dashbuttons.register(s.dash.fairy, fairy_do_something)
dashbuttons.register(s.dash.andrex, andrex_do_something)
server = Server(netopt, dashbuttons)

while True :
    server.GetNextDhcpPacket()

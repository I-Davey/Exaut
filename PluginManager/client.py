import socket
import struct
import select
import time
import json
import traceback
import math

from Plugins import *


class Client:
	""" 
	This class holds all data relevant to clients. 
	in here, we will also put the sockets. this allows the client class to send and receive packets
	from a design persepctive, this also makes sense since this can scale to clientless by just removing server -> client socket
	"""

	def __init__(self, pm: PluginManager, bullets: dict, names: dict, tiles: dict, aoes: dict):

		# some parameters used throught the game
		
		self.pluginManager = pm


	def routePacket(self, packet: Packet, send, onPacketType) -> (Packet, bool):

		p, send = onPacketType(packet, send)

		# if this certain packet has a hook present (meaning it's used by some plugin)
		if packet.ID in self.pluginManager.hooks:

			# then we search for the plugin, and whether if it's active or not.
			for plugin in self.pluginManager.hooks[packet.ID]:
				# if the plugin is active
				if self.pluginManager.plugins[plugin]:
					# at each step, we are editing the packet on the wire
					# important: make sure you're spelling your class methods correctly.
					p, send = getattr(plugin, "on" + PacketTypes.reverseDict[packet.ID])(self, p, send)
					modified = True

		packet = CreatePacket(p)
		return (packet, send)



	def turnOffInjectedStatuses(self):

		for plugin in self.pluginManager.plugins:
			if self.disableSpeedy and type(plugin).__name__ == "Speedy":
				plugin.shutdown(self)
				self.disableSpeedy = False

			elif self.disableSwiftness and type(plugin).__name__ == "Swiftness":
				plugin.shutdown(self)
				self.disableSwiftness = False

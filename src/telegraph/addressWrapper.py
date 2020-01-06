import configparser
import setup

class Destination:

	def __init__(self, callsign, errorCallback, dbgEnabled):
		self.contacts = configparser.ConfigParser()
		self.contacts.read(setup.CONTACTS_FILE)
		self.groups = configparser.ConfigParser()
		self.groups.read(setup.GROUPS_FILE)

		self.callsign = callsign
		self.errorCallback = errorCallback
		self.dbgEnabled = dbgEnabled
		self.dests = self.getDestsFromSign(callsign)

		self.isGroup = None
		self.name = None
		self.members = []

	def debug(self, message):
		if self.dbgEnabled:
			print(message)

	def getAddress(self):
		return self.dests

	def toString(self):
		if self.isGroup is None:
			self.errorCallback("Call sign not found")
			return None
		elif self.isGroup:
			return self.name + ": " + ", ".join(self.members)
		else:
			return self.name

	def getDestsFromSign(self, sign):
		signString = "".join([str(int(symbol)) for symbol in sign])

		dests = []
		if self.contacts.has_section(signString):
			config = self.contacts[signString]
			self.name = config["Name"]
			self.isGroup = False

		elif self.groups.has_section(signString):
			config = self.groups[signString]
			self.name = config["Name"]

			for member in config["Members"]:
				if not self.groups.has_section(member):
					self.debug("Group member not found; continuing.")
					continue
				memberConfig = self.groups[member]
				self.members.append(memberConfig["Name"])
				dests.append((memberConfig["Address"], memberConfig["Port"]))
			self.isGroup = True

		else:
			self.errorCallback("Call sign not found")






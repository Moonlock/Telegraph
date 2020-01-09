from setup import CONTACTS_FILE, GROUPS_FILE
from src.telegraphFunctions import toMorse, writeConfig


class Destination:

	def __init__(self, callsign, errorCallback, dbgEnabled, contactsConfig):
		self.contactsConfig = contactsConfig

		self.callsign = callsign
		self.errorCallback = errorCallback
		self.dbgEnabled = dbgEnabled

		self.config = None
		self.members = []
		self.endpoints = []

	def debug(self, message):
		if self.dbgEnabled:
			print(message)

	def getName(self):
		return self.config["Name"]

	def getSign(self):
		return self.config["Sign"]

	def getEndpoints(self):
		return self.endpoints


class Contact(Destination):

	def __init__(self, callsign, errorCallback, dbgEnabled, contactsConfig):
		Destination.__init__(self, callsign, errorCallback, dbgEnabled, contactsConfig)
		self._parseConfig()

	def getMemberCallsigns(self):
		self.errorCallback(self.getName() + " is not a group.")

	def getAddress(self):
		return self.config["Address"]

	def getPort(self):
		return self.config["Port"]

	def update(self, newConfig):
		self.contactsConfig.remove_section(self.callsign)
		if newConfig is not None:
			self.contactsConfig[toMorse(newConfig["Sign"])] = newConfig

		writeConfig(CONTACTS_FILE, self.contactsConfig)

	def _parseConfig(self):
		signString = "".join([str(int(symbol)) for symbol in self.callsign])

		self.config = self.contactsConfig[signString]
		self.endpoints = [(self.config["Address"], self.config["Port"])]

class Group(Destination):

	def __init__(self, callsign, errorCallback, dbgEnabled, contactsConfig, groupsConfig):
		Destination.__init__(self, callsign, errorCallback, dbgEnabled, contactsConfig)

		self.groupsConfig = groupsConfig
		self._parseConfig()

	def getMemberCallsigns(self):
		return [member.getSign() for member in self.members]

	def update(self, newConfig):
		self.groupsConfig.remove_section(self.callsign)
		if newConfig is not None:
			self.groupsConfig[toMorse(newConfig["Sign"])] = newConfig

		writeConfig(GROUPS_FILE, self.groupsConfig)

	def _parseConfig(self):
		signString = "".join([str(int(symbol)) for symbol in self.callsign])

		self.config = self.groupsConfig[signString]

		for member in self.config["Members"].split():
			if not self.contactsConfig.has_section(member):
				self.debug("Group member not found; continuing.")
				continue
			memberConfig = self.contactsConfig[member]
			self.members.append(Contact(member, self.errorCallback, self.dbgEnabled, self.contactsConfig))
			self.endpoints.append((memberConfig["Address"], memberConfig["Port"]))
		self.isGroup = True












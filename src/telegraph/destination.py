from src import constants
from src.commonFunctions import toMorse


class Destination:

	def __init__(self, callsign, errorCallback, contactsConfig, updater):
		self.updater = updater
		self.contactsConfig = contactsConfig

		self.callsign = callsign
		self.errorCallback = errorCallback

		self.config = None
		self.members = []
		self.endpoints = []

	def getName(self):
		return self.config["Name"]

	def getSign(self):
		return self.config["Sign"]

	def getEndpoints(self):
		return self.endpoints


class Contact(Destination):

	def __init__(self, callsign, errorCallback, contactsConfig, updater):
		Destination.__init__(self, callsign, errorCallback, contactsConfig, updater)
		self._parseConfig()

	def getAddress(self):
		return self.config["Address"]

	def getPort(self):
		return self.config["Port"]

	def getMemberCallsigns(self):
		self.errorCallback(self.getName() + " is not a group.")

	def toString(self):
		return self.getName()

	def update(self, newConfig):
		self.updater.updateConfig(self.callsign, newConfig)

	def _parseConfig(self):
		signString = "".join([str(int(symbol)) for symbol in self.callsign])

		self.config = self.contactsConfig[signString]
		self.endpoints = [(self.config["Address"], self.config["Port"])]


class Group(Destination):

	def __init__(self, callsign, errorCallback, contactsConfig, groupsConfig, updater):
		Destination.__init__(self, callsign, errorCallback, contactsConfig, updater)

		self.groupsConfig = groupsConfig
		self._parseConfig()

	def getMemberCallsigns(self):
		return [member.getSign() for member in self.members]

	def toString(self):
		return self.getName() + ": " + ", ".join([member.getName() for member in self.members])

	def update(self, newConfig):
		self.updater.updateGroup(self.callsign, newConfig)

	def _parseConfig(self):
		signString = "".join([str(int(symbol)) for symbol in self.callsign])

		self.config = self.groupsConfig[signString]

		for member in self.config["Members"].split(' '):
			if not self.contactsConfig.has_section(member):
				print("Group member not found; continuing.")
				continue
			memberConfig = self.contactsConfig[member]
			self.members.append(Contact(member, self.errorCallback, self.contactsConfig, self.updater))
			self.endpoints.append((memberConfig["Address"], memberConfig["Port"]))

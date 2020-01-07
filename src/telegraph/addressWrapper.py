import configparser
from setup import CONTACTS_FILE, GROUPS_FILE


CONTACTS = configparser.ConfigParser()
CONTACTS.read(CONTACTS_FILE)
GROUPS = configparser.ConfigParser()
GROUPS.read(GROUPS_FILE)


class Destination:

	def __init__(self, callsign, errorCallback, dbgEnabled):
		self.callsign = callsign
		self.errorCallback = errorCallback
		self.dbgEnabled = dbgEnabled

		self.isGroup = None
		self.config = None
		self.members = []

		self.dests = self.getDestsFromSign(callsign)

	def debug(self, message):
		if self.dbgEnabled:
			print(message)

	def getName(self):
		return self.config["Name"]

	def getSign(self):
		return self.config["Sign"]

	def getAddress(self):
		return self.dests

	def getMemberCallsigns(self):
		if self.isGroup:
			return [member.getSign() for member in self.members]
		self.errorCallback(self.getName() + " is not a group.")

	def addressString(self):
		if self.isGroup:
			return self.config["Address"] + ":" + self.config["Port"]
		return ", ".join([address[0] + ":" + address[1] for address in self.dests])

	def isGroup(self):
		return self.isGroup

	def toString(self):
		if self.isGroup is None:
			self.errorCallback("Call sign not found")
			return None
		elif self.isGroup:
			return self.getName() + ": " + ", ".join(member.getName() for member in self.members)
		else:
			return self.getName()

	def getDestsFromSign(self, sign):
		signString = "".join([str(int(symbol)) for symbol in sign])

		if CONTACTS.has_section(signString):
			self.config = CONTACTS[signString]
			self.isGroup = False
			return [(self.config["Address"], self.config["Port"])]

		elif GROUPS.has_section(signString):
			self.config = GROUPS[signString]
			dests = []

			for member in self.config["Members"]:
				if not GROUPS.has_section(member):
					self.debug("Group member not found; continuing.")
					continue
				memberConfig = GROUPS[member]
				self.members.append(Destination(memberConfig['code']))
				dests.append((memberConfig["Address"], memberConfig["Port"]))
			self.isGroup = True
			return dests

		else:
			self.errorCallback("Call sign not found")
			return None

	def update(self, newConfig):
		if self.isGroup:
			parser = GROUPS
			filename = GROUPS_FILE
		else:
			parser = CONTACTS
			filename = CONTACTS_FILE

		parser.remove_section(self.callsign)

		if newConfig is not None:
			parser[newConfig["Code"]] = newConfig

		try:
			with open(filename, 'w') as configFile:
				parser.write(configFile)
		except IOError:
			self.errorCallback("Failed to update " + filename + ".")

		print("Successfully updated contacts.")

	@staticmethod
	def getAllContacts(errorCallback):
		return [Destination(callsign, errorCallback, True) for callsign in CONTACTS.sections()]

	@staticmethod
	def getAllGroups(errorCallback):
		return [Destination(callsign, errorCallback, True) for callsign in GROUPS.sections()]

	@staticmethod
	def add(newDestination, isGroup, errorCallback):		#TODO: Fix repeated code.
		if isGroup:
			parser = GROUPS
			filename = GROUPS_FILE
		else:
			parser = CONTACTS
			filename = CONTACTS_FILE

		parser[newDestination["Code"]] = newDestination

		try:
			with open(filename, 'w') as configFile:
				parser.write(configFile)
		except IOError:
			errorCallback("Failed to update " + filename + ".")

		print("Successfully updated contacts.")




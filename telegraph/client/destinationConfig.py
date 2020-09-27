import configparser

from telegraph.client.destination import Contact, Group
from telegraph.common import constants
from telegraph.common.commonFunctions import toMorse, writeConfig


class DestinationConfig:

	def __init__(self, errorCallback, contactsFile=constants.CONTACTS_FILE, groupsFile=constants.GROUPS_FILE):
		self.contactsFile = contactsFile
		self.groupsFile = groupsFile

		self.contactsConfig = configparser.ConfigParser()
		self.contactsConfig.read(self.contactsFile)
		self.groupsConfig = configparser.ConfigParser()
		self.groupsConfig.read(self.groupsFile)

		self.errorCallback = errorCallback

	def createDestination(self, callsign):
		signString = "".join([str(int(symbol)) for symbol in callsign])

		if self.contactsConfig.has_section(signString):
			return Contact(callsign, self.errorCallback, self.contactsConfig, self)
		elif self.groupsConfig.has_section(signString):
			return Group(callsign, self.errorCallback, self.contactsConfig, self.groupsConfig, self)
		else:
			self.errorCallback("Call sign not found")

	def getAllContacts(self):
		return [Contact(callsign, self.errorCallback, self.contactsConfig, self) for callsign in self.contactsConfig.sections()]

	def getAllGroups(self):
		return [Group(callsign, self.errorCallback, self.contactsConfig, self.groupsConfig, self) for callsign in self.groupsConfig.sections()]

	def addContact(self, newContact):
		self.contactsConfig[toMorse(newContact["Sign"])] = newContact
		writeConfig(self.contactsFile, self.contactsConfig)

	def updateContact(self, oldCallsign, newConfig):
		self.contactsConfig.remove_section(oldCallsign)
		if newConfig is not None:
			self.contactsConfig[toMorse(newConfig["Sign"])] = newConfig

		writeConfig(self.contactsFile, self.contactsConfig)

	def addGroup(self, newGroup):
		self.groupsConfig[toMorse(newGroup["Sign"])] = newGroup
		writeConfig(self.groupsFile, self.groupsConfig)

	def updateGroup(self, oldCallsign, newConfig):
		self.groupsConfig.remove_section(oldCallsign)
		if newConfig is not None:
			self.groupsConfig[toMorse(newConfig["Sign"])] = newConfig

		writeConfig(self.groupsFile, self.groupsConfig)










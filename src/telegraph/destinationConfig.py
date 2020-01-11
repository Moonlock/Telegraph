import configparser
from setup import CONTACTS_FILE, GROUPS_FILE
from src.commonFunctions import toMorse, writeConfig
from src.telegraph.destination import Contact, Group


class DestinationConfig:

	def __init__(self, errorCallback):
		self.contactsConfig = configparser.ConfigParser()
		self.contactsConfig.read(CONTACTS_FILE)
		self.groupsConfig = configparser.ConfigParser()
		self.groupsConfig.read(GROUPS_FILE)

		self.errorCallback = errorCallback

	def createDestination(self, callsign):
		signString = "".join([str(int(symbol)) for symbol in self.callsign])

		if self.contactsConfig.has_section(signString):
			return Contact(callsign, self.errorCallback, self.contactsConfig)
		elif self.groupsConfig.has_section(signString):
			return Group(callsign, self.errorCallback, self.contactsConfig, self.groupsConfig)
		else:
			self.errorCallback("Call sign not found")

	def getAllContacts(self):
		return [Contact(callsign, self.errorCallback, self.contactsConfig) for callsign in self.contactsConfig.sections()]

	def getAllGroups(self):
		return [Group(callsign, self.errorCallback, self.contactsConfig, self.groupsConfig) for callsign in self.groupsConfig.sections()]

	def addContact(self, newContact):
		self.contactsConfig[toMorse(newContact["Sign"])] = newContact
		writeConfig(CONTACTS_FILE, self.contactsConfig)

	def addGroup(self, newGroup):
		self.groupsConfig[toMorse(newGroup["Sign"])] = newGroup
		writeConfig(GROUPS_FILE, self.groupsConfig)










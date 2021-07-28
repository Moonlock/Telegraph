import configparser
import socket

from telegraph.common import constants
from telegraph.common.commonFunctions import toMorse, writeConfig
from telegraph.destinations.destination import Contact, Group


class DestinationConfig:

	def __init__(self, contactsFile=constants.CONTACTS_FILE, groupsFile=constants.GROUPS_FILE):
		self.contactsFile = contactsFile
		self.groupsFile = groupsFile

		self.contactsConfig = configparser.ConfigParser()
		self.contactsConfig.read(self.contactsFile)
		self.groupsConfig = configparser.ConfigParser()
		self.groupsConfig.read(self.groupsFile)

	def createDestination(self, callsign):
		signString = "".join([str(int(symbol)) for symbol in callsign])

		if self.contactsConfig.has_section(signString):
			return Contact(callsign, self.contactsConfig, self)
		if self.groupsConfig.has_section(signString):
			return Group(callsign, self.contactsConfig, self.groupsConfig, self)
		return None

	def lookupAddress(self, address):
		try:
			hostname = socket.gethostbyaddr(address)[0]
		except:
			hostname = None

		for contact in self.contactsConfig.sections():
			contactAddress = self.contactsConfig[contact]['Address']
			if contactAddress == address or contactAddress == hostname:
				return self.contactsConfig[contact]['Name']
		return address

	def getAllContacts(self):
		return [Contact(callsign, self.contactsConfig, self) for callsign in self.contactsConfig.sections()]

	def getAllGroups(self):
		return [Group(callsign, self.contactsConfig, self.groupsConfig, self) for callsign in self.groupsConfig.sections()]

	def addContact(self, newContact):
		#TODO: Ask to overwrite if duplicate
		self.contactsConfig[toMorse(newContact["Sign"])] = newContact
		writeConfig(self.contactsFile, self.contactsConfig)

	def updateContact(self, oldCallsign, newConfig):
		self.contactsConfig.remove_section(oldCallsign)
		if newConfig is not None:
			self.contactsConfig[toMorse(newConfig["Sign"])] = newConfig

		writeConfig(self.contactsFile, self.contactsConfig)

	def addGroup(self, newGroup):
		#TODO: Ask to overwrite if duplicate
		self.groupsConfig[toMorse(newGroup["Sign"])] = newGroup
		writeConfig(self.groupsFile, self.groupsConfig)

	def updateGroup(self, oldCallsign, newConfig):
		self.groupsConfig.remove_section(oldCallsign)
		if newConfig is not None:
			self.groupsConfig[toMorse(newConfig["Sign"])] = newConfig

		writeConfig(self.groupsFile, self.groupsConfig)










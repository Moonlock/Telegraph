#! /usr/bin/python3

from src.telegraph.destinationConfig import DestinationConfig
from src.telegraph.destination import Group
from src.telegraphFunctions import toMorse
import setup

import configparser
import sys

# TODO: Removing a contact or changing their call sign will cause an error
#	if they're in a group.

# TODO: Check for duplicate call signs when creating/updating.

def error(message):
	print(message)
	sys.exit()


destConfig = DestinationConfig(True, error)

def main():
	config = configparser.ConfigParser()
	config.read(setup.CONFIG_FILE)
	if config.sections() and not config['Client'].getboolean('Multiple Destinations'):
		print()
		print('Warning: Multiple destinations is disabled- contacts and groups will be ignored.')

	try:
		while True:
			mainloop()
	except KeyboardInterrupt:
		sys.exit()


def mainloop():
	contacts = destConfig.getAllContacts()
	groups = destConfig.getAllGroups()
	idToConfigMap = {i:dest for i, dest in enumerate(contacts + groups)}

	displayMenu(contacts, groups)
	selection = input(" > ")

	while not selection:
		selection = input(" > ")

	if selection.upper() == 'C':
		print("Creating new contact.")
		contactConfig = createNewContact()
		destConfig.addContact(contactConfig)
		return

	if selection.upper() == 'G':
		print("Creating new group.")
		groupConfig = createNewGroup()
		destConfig.addGroup(groupConfig)
		return

	if selection.upper() == 'D':
		deleteDestination(idToConfigMap)
		return

	if selection.upper() == 'Q':
		sys.exit()

	dest = getConfigFromSelection(selection, idToConfigMap)
	if(isinstance(dest, Group)):
		editGroup(dest)
	else:
		editContact(dest)

def displayMenu(contacts, groups):

	i=0

	print()
	print("          ~CONTACTS~")
	for contact in contacts:
		print("    " + str(i) + ": " + contact.getName())
		print("        " + contact.getSign() )#+ "\t" + contact.addressString())
		i += 1

	print()
	print("          ~GROUPS~")
	for group in groups:
		print("    " + str(i) + ": " + group.getName())
		print("        " + group.getSign() + "\t" +
			", ".join(group.getMemberCallsigns()))
		i += 1

	print()
	print("    C: Create new contact")
	print("    G: Create new group")
	print("    D: Delete contact")
	print("    Q: Quit")
	print()

def createNewContact(oldContact=None):

	contactConfig = {}
	contactConfig["Name"] = input("Name")
	contactConfig["Sign"] = input("Call sign").upper()
	contactConfig["Address"] = input("IP Address")
	contactConfig["Port"] = input("Port")
	print("")

	return contactConfig

def editContact(contact):
	print("Editing contact " + contact.getName() + ".")

	newConfig = {}
	newConfig["Name"] = input("Name [" + contact.getName() + "]: ") or contact.getName()
	newConfig["Sign"] = input("Call sign [" + contact.getSign() + "]: ").upper() or contact.getSign()
	newConfig["Address"] = input("IP Address [" + contact.getAddress() + "]: ") or contact.getAddress()
	newConfig["Port"] = input("Port [" + contact.getPort() + "]: ") or contact.getPort()

	contact.update(newConfig)

def createNewGroup():
	groupConfig = {}
	groupConfig["Name"] = input("Group name: ")
	sign = input("Call sign: ").upper()
	groupConfig["Sign"] = sign
	groupConfig["Members"] = getMembers()
	print("")

	return groupConfig

def editGroup(group):
	print("Editing group " + group.getName() + ".")

	newGroup = {}
	newGroup["Name"] = input("Group name [" + group.getName() + "]: ") or group.getName()
	newGroup["Sign"] = input("Call sign [" + group.getSign() + "]: ").upper() or group.getSign()
	newGroup["Members"] = getMembers(group.getMemberCallsigns()) or group.getMemberCallsigns()

	group.update(newGroup)

def getMembers(oldList=None):
	contacts = destConfig.getAllContacts()

	print()
	for contact in contacts:
		print("    " + contact.getSign() + ": " + contact.getName())
	print()

	print("Enter call signs of members, separated by spaces:")
	if oldList:
		print("    [" + " ".join(oldList) + "]")
	members = input(" > ")

	memberList = []
	for member in [m.upper() for m in members.split()]:
		if not member in [contact.getSign() for contact in contacts]:
			print("Error: " + member + " is not in contacts list; not adding to group.")
		else:
			code = str(toMorse(member))
			memberList.append(code)

	return " ".join(memberList)

def deleteDestination(idToConfigMap):
	selection = input(" Delete which contact/group? ")
	if selection == "":
		return

	config = getConfigFromSelection(selection, idToConfigMap)
	print("Deleting " + config.getName() + ".")
	config.update(None)

def getConfigFromSelection(selection, idToConfigMap):
	try:
		userNum = int(selection)
	except ValueError:
		error("Invalid selection.")
	if userNum < 0 or userNum >= len(idToConfigMap):
		error("Invalid selection.")

	return idToConfigMap[userNum]

if __name__ == '__main__':
	main()

#! /usr/bin/python3

from src.learnMorse.alphabet import morse
from src.symbols import Symbol
from src.telegraph.addressWrapper import Destination
import setup

import configparser
import sys

# TODO: Removing a contact or changing their call sign will cause an error
#	if they're in a group.

# TODO: Check for duplicate call signs when creating/updating.

def error(message):
	print(message)
	sys.exit()

def main():
	config = configparser.ConfigParser()
	config.read(setup.CONFIG_FILE)
	if config.sections() and not config['Client'].getboolean('Multiple Destinations'):
		print()
		print('Warning: Multiple destinations is disabled- contacts and groups will be ignored.')

	global _contacts
	_contacts = configparser.ConfigParser()
	_contacts.read(setup.CONTACTS_FILE)

	global _groups
	_groups = configparser.ConfigParser()
	_groups.read(setup.GROUPS_FILE)

	try:
		while True:
			mainloop()
	except KeyboardInterrupt:
		sys.exit()


def mainloop():
	contacts = Destination.getAllContacts(error)
	groups = Destination.getAllGroups(error)
	idToConfigMap = {i:dest for i, dest in enumerate(contacts + groups)}

	displayMenu(contacts, groups)
	selection = input(" > ")

	while not selection:
		selection = input(" > ")

	if selection.upper() == 'C':
		print("Creating new contact.")
		contactConfig = createNewContact()
		Destination.add(contactConfig, False, error)
		return

	if selection.upper() == 'G':
		print("Creating new group.")
		groupConfig = createNewGroup()
		Destination.add(groupConfig, True, error)
		return

	if selection.upper() == 'D':
		deleteDestination(idToConfigMap)
		return

	if selection.upper() == 'Q':
		sys.exit()

	dest = getConfigFromSelection(selection, idToConfigMap)
	if(dest.isGroup):
		editGroup(dest)
	else:
		editContact(dest)

def displayMenu(contacts, groups):

	i=0

	print()
	print("          ~CONTACTS~")
	for contact in contacts:
		print("    " + str(i) + ": " + contact.getName())
		print("        " + contact.getSign() + "\t" + contact.addressString())
		i += 1

	print()
	print("          ~GROUPS~")
	for group in groups:
		print("    " + str(i) + ": " + group.getName())
		print("        " + group.getSign() + "\t" +
			", ".join(group.members))
		i += 1

	print()
	print("    C: Create new contact")
	print("    G: Create new group")
	print("    D: Delete contact")
	print("    Q: Quit")
	print()

def createNewContact(oldContact=None):

	def getInput(getter, prompt):
		if oldContact is None:
			if prompt == 'Port':
				return input("Port [8000]: ") or 8000
			return input(prompt + ": ")
		return input(prompt + " [" + oldContact.getter() + "]: ") or oldContact.getter()

	contactConfig = {}
	contactConfig["Name"] = getInput(Destination.getName, "Name")
	sign = getInput(Destination.getSign, "Call sign").upper()
	contactConfig["Sign"] = sign
	contactConfig["Code"] = toMorse(sign)
	contactConfig["Address"] = getInput(Destination.getAddress, "IP Address")		#TODO: This is terrible.
	contactConfig["Port"] = getInput(Destination.getAddress, "Port")
	contactConfig["Group"] = False
	print("")

	return contactConfig

def toMorse(sign):
	signMorse = []
	for char in sign:
		signMorse.extend(morse[char])
		signMorse.append(Symbol.CHAR_SPACE)

	# Remove trailing character space
	signMorse = signMorse[:-1]
	return "".join([str(int(m)) for m in signMorse])

def editContact(contact):
	print("Editing contact " + contact.getName + ".")
	newConfig = createNewContact(contact)
	contact.update(newConfig)

def createNewGroup():
	groupConfig = {}
	groupConfig["Name"] = input("Group name: ")
	sign = input("Call sign: ").upper()
	groupConfig["Sign"] = sign
	groupConfig["Code"] = toMorse(sign)
	groupConfig["Members"] = getMembers()
	groupConfig["Group"] = True
	print("")

	return groupConfig

def editGroup(group):
	print("Editing group " + group.getName() + ".")

	newGroup = {}
	newGroup["Name"] = input("Group name [" + group.getName() + "]: ") or group.getName()
	sign = input("Call sign [" + group.getSign() + "]: ") or group.getSign()
	newGroup["Sign"] = sign
	newGroup["Code"] = toMorse(sign)
	newGroup["Members"] = getMembers(group.getMemberCallsigns()) or group.getMemberCallsigns()
	newGroup["Group"] = True

	group.update(newGroup)

def getMembers(oldList=None):
	contacts = Destination.getAllContacts(error)

	print()
	for contact in contacts:
		print("    " + contact.getSign() + ": " + contact.getName())
	print()

	print("Enter call signs of members, separated by spaces:")
	if oldList:
		print("    [" + oldList + "]")
	members = input(" > ")

	memberList = []
	for member in [m.upper() for m in members.split()]:
		if not member in [contact.getSign for contact in contacts]:
			print("Error: " + member + " is not in contacts list; not adding to group.")
		else:
			code = str(toMorse(member))
			memberList.append(code)

	return ",".join(memberList)

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

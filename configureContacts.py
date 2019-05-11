#! /usr/bin/python3

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

	global _destinations
	_destinations = configparser.ConfigParser()
	_destinations.read(setup.DEST_FILE)

	try:
		while True:
			mainloop()
	except KeyboardInterrupt:
		sys.exit()


def mainloop():
	idToConfigMap = displayMenu()
	selection = input(" > ")

	while not selection:
		selection = input(" > ")

	if selection.upper() == 'C':
		print("Creating new contact.")
		contactConfig = createNewContact()
		_destinations[contactConfig["Sign"]] = contactConfig
		updatedestinations()
		return

	if selection.upper() == 'G':
		print("Creating new group.")
		groupConfig = createNewGroup()
		_destinations[groupConfig["Sign"]] = groupConfig
		updatedestinations()
		return

	if selection.upper() == 'D':
		deleteContact(idToConfigMap)
		return

	if selection.upper() == 'Q':
		sys.exit()

	config = getConfigFromSelection(selection, idToConfigMap)
	if(config.getboolean("Group")):
		editGroup(config)
	else:
		editContact(config)

def displayMenu():

	contacts = []
	groups = []
	for entry in _destinations.sections():
		if _destinations[entry].getboolean("Group"):
			groups.append(entry)
		else:
			contacts.append(entry)

	i=0
	idToConfigMap = {}
	print()
	print("          ~CONTACTS~")
	for contact in contacts:
		config = _destinations[contact]
		print("    " + str(i) + ": " + config["Name"])
		print("        " + config["Sign"] + "\t" + config["Address"] + ":" + config["Port"])
		idToConfigMap[i] = config
		i += 1
	print()
	print("          ~GROUPS~")
	for group in groups:
		config = _destinations[group]
		print("    " + str(i) + ": " + config["Name"])
		print("        " + config["Sign"] + "\t" +
			", ".join([_destinations[member]["Name"] for member in config["Members"].split(",")]))
		idToConfigMap[i] = config
		i += 1
	print()
	print("    C: Create new contact")
	print("    G: Create new group")
	print("    D: Delete contact")
	print("    Q: Quit")
	print()

	return idToConfigMap

def createNewContact(userData=None):

	def getInput(section, prompt):
		if userData is None:
			if section == 'Port':
				return input("Port [8000]: ") or 8000
			return input(prompt + ": ")
		return input(prompt + " [" + userData[section] + "]: ") or userData[section]

	contactConfig = {}
	contactConfig["Name"] = getInput("Name", "Name")
	contactConfig["Sign"] = getInput("Sign", "Call sign").upper()
	contactConfig["Address"] = getInput("Address", "IP Address")
	contactConfig["Port"] = getInput("Port", "Port")
	contactConfig["Group"] = False
	print("")

	return contactConfig

def editContact(userData):
	print("Editing contact " + userData['Name'] + ".")
	contactConfig = createNewContact(userData)
	_destinations.remove_section(userData['Sign'])
	_destinations[contactConfig["Sign"]] = contactConfig
	updatedestinations()

def createNewGroup():
	groupConfig = {}
	groupConfig["Name"] = input("Group name: ")
	groupConfig["Sign"] = input("Call sign: ").upper()
	groupConfig["Members"] = getMembers()
	groupConfig["Group"] = True
	print("")

	return groupConfig

def editGroup(groupData):
	print("Editing group " + groupData['Name'] + ".")
	newGroup = {}
	newGroup["Name"] = input("Group name [" + groupData["Name"] + "]: ") or groupData["Name"]
	newGroup["Sign"] = input("Call sign [" + groupData["Sign"] + "]: ") or groupData["Sign"]
	newGroup["Members"] = getMembers(groupData["Members"]) or groupData["Members"]
	newGroup["Group"] = True

	_destinations.remove_section(groupData["Sign"])
	_destinations[newGroup["Sign"]] = newGroup
	updatedestinations()

def getMembers(oldList=None):
	contacts = []
	for entry in _destinations.sections():
		if not _destinations[entry].getboolean("Group"):
			contacts.append(entry)

	print()
	for contact in contacts:
		userData = _destinations[contact]
		print("    " + contact + ": " + userData["Name"])
	print()

	print("Enter call signs of members, separated by spaces:")
	if oldList:
		print("    [" + oldList + "]")
	members = input(" > ")
	memberList = []
	for member in [m.upper() for m in members.split()]:
		if not member in _destinations.sections():
			print("Error: " + member + " is not in contacts list; not adding to group.")
		else:
			memberList.append(member)
	return ",".join(memberList)

def deleteContact(idToConfigMap):
	selection = input(" Delete which contact? ")
	if selection == "":
		return

	config = getConfigFromSelection(selection, idToConfigMap)
	print("Deleting contact " + config['Name'] + ".")
	_destinations.remove_section(config["Sign"])
	updatedestinations()

def getConfigFromSelection(selection, idToConfigMap):
	try:
		userNum = int(selection)
	except ValueError:
		error("Invalid selection.")
	if userNum < 0 or userNum >= len(idToConfigMap):
		error("Invalid selection.")

	return idToConfigMap[userNum]

def updatedestinations():
	try:
		with open(setup.DEST_FILE, 'w') as configFile:
			_destinations.write(configFile)
	except IOError:
		error("Failed to update contacts.")

	print("Successfully updated contacts.")

if __name__ == '__main__':
	main()
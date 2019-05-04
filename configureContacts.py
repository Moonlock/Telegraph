#! /usr/bin/python3

import setup

import configparser
import sys

def error(message):
	print(message)
	sys.exit()

def main():
	config = configparser.ConfigParser()
	config.read(setup.CONFIG_FILE)
	if config.sections() and config['Client']['singleDest']:
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
	displayMenu()
	selection = input(" > ")

	while not selection:
		selection = input(" > ")

	if selection.upper() == 'N':
		print("Creating new contact.")
		(callSign, contactConfig) = createNewContact()
		_destinations[callSign] = contactConfig
		updatedestinations()
		return

	if selection.upper() == 'D':
		deleteContact()
		return

	if selection.upper() == 'Q':
		sys.exit()

	editContact(selection)

def displayMenu():
	i=0
	print()
	for user in _destinations.sections():
		userData = _destinations[user]
		print("    " + str(i) + ": " + userData["Name"])
		print("        " + user + "\t" + userData["Address"] + ":" + userData["Port"])
		i += 1
	print()
	print("    N: Create new contact")
	print("    D: Delete contact")
	print("    Q: Quit")
	print()

def createNewContact(userData=None):

	def getInput(section, prompt):
		if userData is None:
			if section == 'Port':
				return input("Port [8000]: ") or 8000
			return input(prompt + ": ")
		return input(prompt + " [" + userData[section] + "]: ") or userData[section]

	contactConfig = {}
	contactConfig["Name"] = getInput("Name", "Name")
	callSign = getInput("Sign", "Call sign").upper()
	contactConfig["Sign"] = callSign
	contactConfig["Address"] = getInput("Address", "IP Address")
	contactConfig["Port"] = getInput("Port", "Port")
	print("")

	return (callSign, contactConfig)

def editContact(selection):
	key = getKeyFromSelection(selection, len(_destinations.sections()))
	userData = _destinations[key]

	print("Editing contact " + userData['Name'] + ".")
	(callSign, contactConfig) = createNewContact(userData)
	_destinations.remove_section(key)
	_destinations[callSign] = contactConfig
	updatedestinations()

def deleteContact():
	selection = input(" Delete which contact? ")
	if selection == "":
		return

	key = getKeyFromSelection(selection, len(_destinations.sections()))
	print("Deleting contact " + _destinations[key]['Name'] + ".")
	_destinations.remove_section(key)
	updatedestinations()

def getKeyFromSelection(selection, numOptions):
	try:
		userNum = int(selection)
	except ValueError:
		error("Invalid selection.")
	if userNum < 0 or userNum >= numOptions:
		error("Invalid selection.")

	return _destinations.sections()[userNum]

def updatedestinations():
	try:
		with open(setup.DEST_FILE, 'w') as configFile:
			_destinations.write(configFile)
	except IOError:
		error("Failed to update contacts.")

	print("Successfully updated contacts.")

if __name__ == '__main__':
	main()

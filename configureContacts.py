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

	try:
		while getUserData():
			pass
	except KeyboardInterrupt:
		sys.exit()

def createNewContact(config, userData=None):

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

def getUserData():
	config = configparser.ConfigParser()
	config.read(setup.DEST_FILE)
	sections = config.sections()
	i=0
	print()
	for user in sections:
		userData = config[user]
		print("    " + str(i) + ": " + userData["Name"])
		print("        " + user + "\t" + userData["Address"] + ":" + userData["Port"])
		i += 1
	print()
	print("    N: Create new contact")
	print("    D: Delete contact")
	print("    Q: Quit")
	print()
	selection = input(" > ")

	def getNameFromSelection(selection):
		try:
			userNum = int(selection)
		except ValueError:
			error("Invalid selection.")
		if userNum < 0 or userNum >= i:
			error("Invalid selection.")

		return sections[userNum]

	while not selection:
		selection = input(" > ")

	if selection.upper() == 'N':
		print("Creating new contact.")
		(callSign, contactConfig) = createNewContact(config)
		config[callSign] = contactConfig

	elif selection.upper() == 'D':
		selection = input(" Delete which contact? ")
		if selection == "":
			return True

		name = getNameFromSelection(selection)
		print("Deleting contact " + name + ".")
		config.remove_section(name)

	elif selection.upper() == 'Q':
		return False

	else:
		name = getNameFromSelection(selection)
		userData = config[name]

		(callSign, contactConfig) = createNewContact(config, userData)
		config.remove_section(name)
		config[callSign] = contactConfig

	try:
		with open(setup.DEST_FILE, 'w') as configFile:
			config.write(configFile)
	except IOError:
		error("Failed to update contacts.")

	print("Successfully updated contacts.")

	return True

if __name__ == '__main__':
	main()

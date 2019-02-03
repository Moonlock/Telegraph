#! /usr/bin/python3

import configparser
import sys

USERS_FILE = 'src/learnMorse/users.ini'

def error(message):
	print(message)
	sys.exit()

def createNewUser(config):
	print("Creating new user.")
	username = input("Username: ")

	userConfig = {}
	userConfig["Characters"] = input('Initial number of characters [2]: ') or 2
	userConfig["Character WPM"] = input('Character WPM speed [20]: ') or 20
	userConfig["Overall WPM"] = input('Overall WPM with Farnsworth timing [10]: ') or 10
	userConfig["Time"] = input('Test time in seconds [300]: ') or 300
	print("")

	config[username] = userConfig
	try:
		with open(USERS_FILE, 'w') as configFile:
			config.write(configFile)
	except IOError:
		error("Failed to update users file.")

	return userConfig

def getUserData():
	config = configparser.ConfigParser()
	config.read(USERS_FILE)
	sections = config.sections()
	i=0
	print()
	for user in sections:
		print("    " + str(i) + ": " + user)
		i += 1
	print()
	print("    N: Create new user")
	print()
	selection = input(" > ")

	if selection.upper() == 'N':
		return createNewUser(config)

	try:
		userNum = int(selection)
	except IOError:
		error("Invalid selection.")
	if userNum < 0 or userNum >= i:
		error("Invalid selection.")

	return config[sections[userNum]]

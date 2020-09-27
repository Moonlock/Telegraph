#! /usr/bin/python3

import configparser

from src.commonFunctions import fatal, writeConfig


USERS_FILE = 'src/learnMorse/users.ini'

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
	writeConfig(USERS_FILE, config)

	return (username, userConfig)

def increaseCharacters(user):
	config = configparser.ConfigParser()
	config.read(USERS_FILE)
	if not config.has_section(user):
		fatal("Failed to update user file: User " + user + " does not exist.")

	numChars = config.getint(user, "Characters")
	if(numChars == 36):
		print("Number of Characters is already at maximum.")
		return
	numChars += 1

	print("Increasing number of characters.")
	config[user]["Characters"] = str(numChars)
	writeConfig(USERS_FILE, config)

	print("Number of characters is now " + str(numChars))

def getUserData():
	config = configparser.ConfigParser()
	config.read(USERS_FILE)
	sections = config.sections()
	i=0
	print()
	print("Select user:")
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
		fatal("Invalid selection.")
	if userNum < 0 or userNum >= i:
		fatal("Invalid selection.")

	user = sections[userNum]
	return (user, config[user])

#! /usr/bin/python3
import sys
import configparser
from learnMorse import learnMorse

def error(message):
	print(message)
	exit()

def createNewUser():
	print("Creating new user.")
	username = input("Username: ")

	userConfig = {}
	userConfig["Characters"] = input('Initial number of characters [2]: ') or 2
	userConfig["Character WPM"] = input('Character WPM speed [20]: ') or 20
	userConfig["Overall WPM"] = input('Overall WPM with Farnsworth timing [10]: ') or 10
	userConfig["Time"] = input('Test time in seconds [300]: ') or 300

	config[username] = userConfig
	try:
		with open('users.ini', 'w') as configFile:
			config.write(configFile)
	except IOError:
		error("Failed to update users file.")

	return userConfig


config = configparser.ConfigParser()
config.read("users.ini")
sections = config.sections()
i=0
print("")
for user in sections:
	print("    " + str(i) + ": " + user)
	i += 1
print("    " + str(i) + ": Create new user")
print("")
try:
	selection = int(input(" > "))
except:
	error("Invalid selection.")
if selection < 0 or selection > i:
	error("Invalid selection.")

if selection == i:
	userConfig = createNewUser()
else:
	userConfig = config[sections[selection]]

charWpm = int(userConfig["Character WPM"])
overallWpm = int(userConfig["Overall WPM"])
numChars = int(userConfig["Characters"])
testTime = int(userConfig["Time"])

learnMorse.morseTest(charWpm, overallWpm, numChars, testTime)

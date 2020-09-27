#! /usr/bin/python3

import sys

from src.learnMorse import users
from src.learnMorse.testModes import testModes


try:
	(user, userConfig) = users.getUserData()
	mode = testModes.getTestMode()
except KeyboardInterrupt:
	sys.exit()

charWpm = int(userConfig["Character WPM"])
overallWpm = int(userConfig["Overall WPM"])
numChars = int(userConfig["Characters"])
testTime = int(userConfig["Time"])

mode(charWpm, overallWpm, numChars, testTime, user)

#! /usr/bin/python3

import sys

from telegraph.learnMorse import users
from telegraph.learnMorse.testModes import testModes


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

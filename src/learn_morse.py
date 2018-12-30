#! /usr/bin/python3
from learnMorse import learnMorse, users

try:
	userConfig = users.getUserData()
except KeyboardInterrupt:
	exit()

charWpm = int(userConfig["Character WPM"])
overallWpm = int(userConfig["Overall WPM"])
numChars = int(userConfig["Characters"])
testTime = int(userConfig["Time"])

test = learnMorse.morseTest(charWpm, overallWpm, numChars, testTime)

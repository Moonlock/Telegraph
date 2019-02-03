#! /usr/bin/python3

from src.learnMorse import learnMorse, users
import sys

try:
	userConfig = users.getUserData()
except KeyboardInterrupt:
	sys.exit()

charWpm = int(userConfig["Character WPM"])
overallWpm = int(userConfig["Overall WPM"])
numChars = int(userConfig["Characters"])
testTime = int(userConfig["Time"])

test = learnMorse.morseTest(charWpm, overallWpm, numChars, testTime)

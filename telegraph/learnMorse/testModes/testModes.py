from enum import Enum
from telegraph.common.commonFunctions import fatal
from telegraph.learnMorse.testModes.randomLettersMode import RandomLettersMode
from telegraph.learnMorse.testModes.randomLettersSeparateMode import RandomLettersSeparateMode
from telegraph.learnMorse.testModes.textMode import TextMode

try:
	from telegraph.learnMorse.testModes.sendMorseMode import SendMode
	usingGpio = True
except ImportError:
	usingGpio = False


class TestMode(Enum):
	RANDOM = (0, "Random Letters", RandomLettersMode)
	RANDOM_SEPARATE = (1, "Random Letters (One at a time)", RandomLettersSeparateMode)
	TEXT = (2, "Text (No numbers or punctuation)", TextMode)

	if usingGpio:
		SEND = (3, "Send letters", SendMode)

	def __init__(self, index, description, cls):
		self.index = index
		self.description = description
		self.cls = cls

	@classmethod
	def getByIndex(cls, index):
		for mode in TestMode:
			if index == mode.index:
				return mode
		fatal("Invalid selection")

def getTestMode():
	print()
	print("Select test mode:")
	for mode in TestMode:
		print("    " + str(mode.index) + ": " + mode.description)
	print()
	selection = input(" > ")

	try:
		modeNum = int(selection)
	except IOError:
		fatal("Invalid selection.")

	selectedMode = TestMode.getByIndex(modeNum)
	return selectedMode.cls

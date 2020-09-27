from enum import Enum
from telegraph.common.commonFunctions import fatal
from telegraph.learnMorse.testModes.randomLettersMode import RandomLettersMode
from telegraph.learnMorse.testModes.randomLettersSeparateMode import RandomLettersSeparateMode


class TestMode(Enum):
	RANDOM = (0, "Random Letters", RandomLettersMode)
	RANDOM_SEPARATE = (1, "Random Letters (One at a time)", RandomLettersSeparateMode)

	def __init__(self, index, description, cls):
		self.index = index
		self.description = description
		self.cls = cls

	@classmethod
	def getByIndex(cls, index):
		if index == 0:
			return cls.RANDOM
		elif index == 1:
			return cls.RANDOM_SEPARATE
		else:
			fatal("Invalid Selection")

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
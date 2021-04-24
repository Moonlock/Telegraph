from subprocess import Popen
from time import sleep
import random
import signal
import sys

from telegraph.common.constants import SOUND_FILES_PATH
from telegraph.common.symbols import Symbol
from telegraph.learnMorse.alphabet import morse
from telegraph.learnMorse.testModes.testModeInterface import TestModeInterface, \
		DIT_FILE, DAH_FILE, SYMBOL_SPACE_FILE, CHAR_SPACE_FILE, WORD_SPACE_FILE, TEST_FILE
import telegraph.common.commonFunctions as common


class RandomLettersMode(TestModeInterface):

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		signal.signal(signal.SIGINT, self.handleSigIntNoTimer)

		self.masterList = []
		self.user = user
		self.createSymbolFiles(charWpm, overallWpm)

		self.chars = []
		for _ in range(numChars):
			self.chars.append(morse.popitem(False))

		self.testTime = testTime

		sleep(2)
		self.startTest()

	def startTest(self):

		print("Enter what you hear:")
		print(" > ", end="")
		sys.stdout.flush()

		timeSpent = 0
		fileList = []

		while timeSpent < self.testTime:

			wordLength = random.choice(range(8)) + 1
			for _ in range(wordLength):
				char = random.choice(self.chars)
				self.masterList.append(char[0])

				for symbol in char[1]:
					if symbol == Symbol.DIT:
						fileList.append(DIT_FILE)
						timeSpent += self.ditLength
					else:
						fileList.append(DAH_FILE)
						timeSpent += self.dahLength
					fileList.append(SYMBOL_SPACE_FILE)
					timeSpent += self.symbolSpace

				fileList.append(CHAR_SPACE_FILE)
				timeSpent += self.charSpace

			fileList.append(WORD_SPACE_FILE)
			timeSpent += self.wordSpace
			self.masterList.append(' ')

		common.concatAudioFiles(fileList, TEST_FILE)
		proc = Popen(['play', '-q', TEST_FILE])

		#Remove final word space
		self.masterList.pop()

		response = input()
		master = "".join(self.masterList)
		print("   " + master)
		self.checkAnswer(response.upper(), master)

		proc.kill()
		common.deleteFiles(SOUND_FILES_PATH, "learnMorse-", ".sox")


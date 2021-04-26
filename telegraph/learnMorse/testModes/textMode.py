from subprocess import Popen
from time import sleep
import os
import random
import signal
import sys

from telegraph.common.constants import SOUND_FILES_PATH
from telegraph.common.symbols import Symbol
from telegraph.learnMorse.alphabet import letters
from telegraph.learnMorse.testModes.testModeInterface import TestModeInterface, \
		DIT_FILE, DAH_FILE, SYMBOL_SPACE_FILE, CHAR_SPACE_FILE, WORD_SPACE_FILE, TEST_FILE, SECONDS_PER_MINUTE
import telegraph.common.commonFunctions as common


APPROX_CHARS_PER_WORD = 5

TEXT_FILES_PATH = "resources/testData/corpus/"

# Offset in text files to skip copyright/table of contents
TEXT_START_OFFSET = 200
END_COPYRIGHT_LENGTH = 400


class TextMode(TestModeInterface):

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		signal.signal(signal.SIGINT, self.handleSigIntNoTimer)

		self.masterList = []
		self.createSymbolFiles(charWpm, overallWpm)

		self.testTime = testTime
		self.wpm = overallWpm

		sleep(2)
		self.startTest()

	def getText(self):
		textFiles = os.listdir(TEXT_FILES_PATH)
		self.chosenFile = random.choice(textFiles)

		with open(TEXT_FILES_PATH + self.chosenFile) as file:
			text = file.read()
		return text;

	def startTest(self):

		print("Enter what you hear:")
		print(" > ", end="")
		sys.stdout.flush()

		timeSpent = 0
		fileList = []

		approxCharsInTest = self.wpm*APPROX_CHARS_PER_WORD * self.testTime/SECONDS_PER_MINUTE

		text = self.getText()
		maxStartingPos = int(len(text) - approxCharsInTest*2 - END_COPYRIGHT_LENGTH)
		pos = random.choice(range(maxStartingPos - TEXT_START_OFFSET)) + TEXT_START_OFFSET

		while timeSpent < self.testTime:

			char = text[pos]

			if (char == ' ' or char == '\n' or char == '-') and self.masterList and self.masterList[-1] != ' ':
				fileList.append(WORD_SPACE_FILE)
				timeSpent += self.wordSpace
				self.masterList.append(' ')

			elif char.upper() in letters:
				self.masterList.append(char)

				for symbol in letters[char.upper()]:
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

			pos += 1
			if pos == len(text):
				pos = 0

		common.concatAudioFiles(fileList, TEST_FILE)
		proc = Popen(['play', '-q', TEST_FILE])

		#Remove trailing whitespace
		if self.masterList[-1] == ' ':
			self.masterList.pop()

		response = input()
		master = "".join(self.masterList)
		print("   " + master)
		print(self.chosenFile)
		self.checkAnswer(response.lower(), master.lower())

		proc.kill()
		common.deleteFiles(SOUND_FILES_PATH, "learnMorse-", ".sox")


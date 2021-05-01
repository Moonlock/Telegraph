from threading import Timer
from time import sleep
import os
import random
import signal
import sys

from telegraph.common.symbols import Symbol
from telegraph.learnMorse.alphabet import letters
from telegraph.learnMorse.testModes.testModeInterface import TestModeInterface, SECONDS_PER_MINUTE


APPROX_CHARS_PER_WORD = 5

TEXT_FILES_PATH = "resources/testData/corpus/"

# Offset in text files to skip copyright/table of contents
TEXT_START_OFFSET = 200
END_COPYRIGHT_LENGTH = 400


class TextMode(TestModeInterface):

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		signal.signal(signal.SIGINT, self.handleSigInt)

		self.masterList = []
		self.initializeTiming(charWpm, overallWpm)

		self.testTime = testTime
		self.wpm = overallWpm

		self.timer = Timer(testTime, self.stopTest)

		sleep(2)
		self.running = True
		self.timer.start()
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

		lines = self.getText().split('\n')
		text = '\n'.join(lines[TEXT_START_OFFSET : -END_COPYRIGHT_LENGTH])

		approxCharsInTest = self.wpm*APPROX_CHARS_PER_WORD * self.testTime/SECONDS_PER_MINUTE
		maxStartingPos = int(len(text) - approxCharsInTest*2)
		pos = random.choice(range(maxStartingPos))

		prevIsChar = False

		while self.running:

			char = text[pos]

			if (char == ' ' or char == '\n' or char == '-') and self.masterList:
				if prevIsChar:
					self.playWordSpace()
					self.masterList.append(' ')
					prevIsChar = False

			elif char.upper() in letters:
				if prevIsChar:
					self.playCharSpace()
				prevIsChar = True

				self.masterList.append(char)

				for symbol in letters[char.upper()]:
					if symbol == Symbol.DIT:
						self.playDit()
					else:
						self.playDah()
					self.playSymbolSpace()

			pos += 1

		#Remove trailing whitespace
		if self.masterList[-1] == ' ':
			self.masterList.pop()

		response = input()
		master = "".join(self.masterList)
		print("   " + master)
		print(self.chosenFile)
		self.checkAnswer(response.lower(), master.lower())


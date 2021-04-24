from subprocess import Popen
from time import sleep
import difflib
import os
import random
import signal
import sys

from telegraph.common.constants import SOUND_FILES_PATH
from telegraph.common.symbols import Symbol
from telegraph.learnMorse.alphabet import letters
from telegraph.learnMorse.testModes.testModeInterface import TestModeInterface
import telegraph.common.commonFunctions as common


COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60
APPROX_CHARS_PER_WORD = 5

DIT_FILE = SOUND_FILES_PATH + "learnMorse-dit.sox"
DAH_FILE = SOUND_FILES_PATH + "learnMorse-dah.sox"
SYMBOL_SPACE_FILE = SOUND_FILES_PATH + "learnMorse-symbol.sox"
CHAR_SPACE_FILE = SOUND_FILES_PATH + "learnMorse-char.sox"
WORD_SPACE_FILE = SOUND_FILES_PATH + "learnMorse-word.sox"
TEST_FILE = SOUND_FILES_PATH + "learnMorse-test.sox"

TEXT_FILES_PATH = "resources/testData/corpus/"

# Offset in text files to skip copyright/table of contents
TEXT_START_OFFSET = 200


class TextMode(TestModeInterface):

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		signal.signal(signal.SIGINT, self.handleSigInt)

		self.masterList = []
		timeUnit = SECONDS_PER_MINUTE / (COUNTS_PER_WORD * charWpm)
		self.ditLength = timeUnit
		self.dahLength = 3*timeUnit
		Popen(['sox', '-n', DIT_FILE, 'synth', str(self.ditLength), 'sin', '900'])
		Popen(['sox', '-n', DAH_FILE, 'synth', str(self.dahLength), 'sin', '900'])

		# Equations from http://www.arrl.org/files/file/Technology/x9004008.pdf
		totalDelay = (60*charWpm - 37.2*overallWpm) / \
					 (charWpm * overallWpm)
		self.symbolSpace = 1.0 / (charWpm/60.0 * COUNTS_PER_WORD)
		self.charSpace = 3*totalDelay / 19 - self.symbolSpace
		self.wordSpace = 7*totalDelay / 19 - self.symbolSpace

		Popen(['sox', '-n', SYMBOL_SPACE_FILE, 'trim', '0', str(self.symbolSpace)])
		Popen(['sox', '-n', CHAR_SPACE_FILE, 'trim', '0', str(self.charSpace)])
		Popen(['sox', '-n', WORD_SPACE_FILE, 'trim', '0', str(self.wordSpace)])

		self.testTime = testTime
		self.wpm = overallWpm

		sleep(2)
		self.startTest()

	def handleSigInt(self, sig, frame):
		common.deleteFiles(SOUND_FILES_PATH, "learnMorse-", ".sox")
		common.deleteFiles(SOUND_FILES_PATH, "temp-", ".sox")
		sys.exit()

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
		maxStartingPos = int(len(text) - approxCharsInTest*2)
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
		self.checkAnswer(response.lower(), master.lower())

		proc.kill()
		common.deleteFiles(SOUND_FILES_PATH, "learnMorse-", ".sox")

	def checkAnswer(self, response, master):
		diff = difflib.SequenceMatcher(None, master, response, autojunk=False)
		score = diff.ratio() * 100
		print()
		print(self.chosenFile)
		print("Score: " + "{:.2f}".format(score) + "%")


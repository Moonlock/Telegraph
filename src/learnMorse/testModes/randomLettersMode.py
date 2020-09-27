from subprocess import Popen
from time import sleep
import difflib
import random
import signal
import sys

from src.constants import SOUND_FILES_PATH
from src.learnMorse import users
from src.learnMorse.alphabet import morse
from src.learnMorse.testModes.testModeInterface import TestModeInterface
from src.symbols import Symbol
import src.commonFunctions as common


COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60

DIT_FILE = SOUND_FILES_PATH + "learnMorse-dit.sox"
DAH_FILE = SOUND_FILES_PATH + "learnMorse-dah.sox"
SYMBOL_SPACE_FILE = SOUND_FILES_PATH + "learnMorse-symbol.sox"
CHAR_SPACE_FILE = SOUND_FILES_PATH + "learnMorse-char.sox"
WORD_SPACE_FILE = SOUND_FILES_PATH + "learnMorse-word.sox"
TEST_FILE = SOUND_FILES_PATH + "learnMorse-test.sox"


class RandomLettersMode(TestModeInterface):

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		signal.signal(signal.SIGINT, self.handleSigInt)

		self.masterList = []
		self.user = user
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

		self.chars = []
		for _ in range(numChars):
			self.chars.append(morse.popitem(False))

		self.testTime = testTime

		sleep(2)
		self.startTest()

	def handleSigInt(self, sig, frame):
		common.deleteFiles(SOUND_FILES_PATH, "learnMorse-", ".sox")
		common.deleteFiles(SOUND_FILES_PATH, "temp-", ".sox")
		sys.exit()

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

		common.createFile(fileList, TEST_FILE)
		proc = Popen(['play', '-q', TEST_FILE])

		#Remove final word space
		self.masterList.pop()

		response = input()
		master = "".join(self.masterList)
		print("   " + master)
		self.checkAnswer(response.upper(), master)

		proc.kill()
		common.deleteFiles(SOUND_FILES_PATH, "learnMorse-", ".sox")

	def checkAnswer(self, response, master):
		diff = difflib.SequenceMatcher(None, master, response, autojunk=False)
		score = diff.ratio() * 100
		print()
		print("Score: " + "{:.2f}".format(score) + "%")
		if score >= 90:
			users.increaseCharacters(self.user)


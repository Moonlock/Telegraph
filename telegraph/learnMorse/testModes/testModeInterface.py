from subprocess import Popen
from sys import exit
import difflib

from telegraph.common.constants import SOUND_FILES_PATH
from telegraph.learnMorse import users
import telegraph.common.commonFunctions as common


COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60

DIT_FILE = SOUND_FILES_PATH + "learnMorse-dit.sox"
DAH_FILE = SOUND_FILES_PATH + "learnMorse-dah.sox"
SYMBOL_SPACE_FILE = SOUND_FILES_PATH + "learnMorse-symbol.sox"
CHAR_SPACE_FILE = SOUND_FILES_PATH + "learnMorse-char.sox"
WORD_SPACE_FILE = SOUND_FILES_PATH + "learnMorse-word.sox"
TEST_FILE = SOUND_FILES_PATH + "learnMorse-test.sox"


class TestModeInterface:

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		pass

	def handleSigIntNoTimer(self, sig, frame):
		common.deleteFiles(SOUND_FILES_PATH, "learnMorse-", ".sox")
		common.deleteFiles(SOUND_FILES_PATH, "temp-", ".sox")
		exit()

	def handleSigIntWithTimer(self, sig, frame):
		common.deleteFiles(SOUND_FILES_PATH, "learnMorse-", ".sox")
		common.deleteFiles(SOUND_FILES_PATH, "temp-", ".sox")
		self.timer.cancel()
		self.running = False

	def checkAnswer(self, response, master, updateUser=False):
		diff = difflib.SequenceMatcher(None, master, response, autojunk=False)
		score = diff.ratio() * 100
		print()
		print("Score: " + "{:.2f}".format(score) + "%")

		if updateUser and score >= 90:
			users.increaseCharacters(self.user)

	def createSymbolFiles(self, charWpm, overallWpm=None):
		timeUnit = SECONDS_PER_MINUTE / (COUNTS_PER_WORD * charWpm)
		self.ditLength = timeUnit
		self.dahLength = 3*timeUnit

		# Equations from http://www.arrl.org/files/file/Technology/x9004008.pdf
		totalDelay = (60*charWpm - 37.2*overallWpm) / \
					 (charWpm * overallWpm)
		self.symbolSpace = timeUnit
		self.charSpace = 3*totalDelay / 19 - self.symbolSpace
		self.wordSpace = 7*totalDelay / 19 - self.symbolSpace

		Popen(['sox', '-n', DIT_FILE, 'synth', str(self.ditLength), 'sin', '900'])
		Popen(['sox', '-n', DAH_FILE, 'synth', str(self.dahLength), 'sin', '900'])
		Popen(['sox', '-n', SYMBOL_SPACE_FILE, 'trim', '0', str(self.symbolSpace)])
		Popen(['sox', '-n', CHAR_SPACE_FILE, 'trim', '0', str(self.charSpace)])
		Popen(['sox', '-n', WORD_SPACE_FILE, 'trim', '0', str(self.wordSpace)])

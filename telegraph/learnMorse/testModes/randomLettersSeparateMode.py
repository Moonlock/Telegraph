from subprocess import Popen
from threading import Timer
from time import sleep
import random
import signal
import sys
import tty

from telegraph.common.constants import SOUND_FILES_PATH
from telegraph.common.symbols import Symbol
from telegraph.learnMorse.alphabet import morse
from telegraph.learnMorse.testModes.testModeInterface import TestModeInterface
import telegraph.common.commonFunctions as common
import termios


COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60

DIT_FILE = SOUND_FILES_PATH + "learnMorse-dit.sox"
DAH_FILE = SOUND_FILES_PATH + "learnMorse-dah.sox"


class RandomLettersSeparateMode(TestModeInterface):

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		signal.signal(signal.SIGINT, self.handleSigInt)

		timeUnit = SECONDS_PER_MINUTE / (COUNTS_PER_WORD * charWpm)
		self.ditLength = timeUnit
		self.dahLength = 3*timeUnit
		Popen(['sox', '-n', DIT_FILE, 'synth', str(timeUnit), 'sin', '900'])
		Popen(['sox', '-n', DAH_FILE, 'synth', str(3*timeUnit), 'sin', '900'])

		self.symbolSpace = 1.0 / (charWpm/60.0 * COUNTS_PER_WORD)

		self.chars = []
		for _ in range(numChars):
			self.chars.append(morse.popitem(False))

		self.testTime = testTime
		self.timer = Timer(testTime, self.stopTest)

		sleep(2)
		self.running = True
		self.timer.start()
		self.startTest()

	def handleSigInt(self, sig, frame):
		common.deleteFiles(SOUND_FILES_PATH, "learnMorse-", ".sox")
		self.timer.cancel()
		self.running = False

	def stopTest(self):
		self.running = False

	def playDit(self):
		Popen(['play', '-q', DIT_FILE])
		sleep(self.ditLength + self.symbolSpace)

	def playDah(self):
		Popen(['play', '-q', DAH_FILE])
		sleep(self.dahLength + self.symbolSpace)

	def getChar(self):
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

		if ch == '\x03':
			self.timer.cancel()
			self.running = False
			return None
		return ch

	def startTest(self):
		play = {
			Symbol.DIT: self.playDit,
			Symbol.DAH: self.playDah,
		}

		correct = 0
		incorrect = 0
		while self.running:
			char = random.choice(self.chars)
			for symbol in char[1]:
				play[symbol]()

			response = self.getChar()

			if response is None:
				continue
			if response.upper() == char[0]:
				correct += 1
			else:
				incorrect += 1
				print(char[0])
				sleep(1)

		print()
		print("Correct: " + str(correct))
		print("Incorrect: " + str(incorrect))
		print("Score: " + str(correct - incorrect))

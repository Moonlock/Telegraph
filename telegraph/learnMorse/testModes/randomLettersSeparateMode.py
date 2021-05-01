from threading import Timer
from time import sleep
import random
import signal
import sys
import tty

from telegraph.common.symbols import Symbol
from telegraph.learnMorse.alphabet import morse
from telegraph.learnMorse.testModes.testModeInterface import TestModeInterface
import termios


class RandomLettersSeparateMode(TestModeInterface):

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		signal.signal(signal.SIGINT, self.handleSigInt)

		self.initializeTiming(charWpm, overallWpm)

		self.chars = []
		for _ in range(numChars):
			self.chars.append(morse.popitem(False))

		self.timer = Timer(testTime, self.stopTest)

		sleep(2)
		self.running = True
		self.timer.start()
		self.startTest()

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
				self.playSymbolSpace()

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

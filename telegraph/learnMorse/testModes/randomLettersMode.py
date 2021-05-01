from threading import Timer
from time import sleep
import random
import signal
import sys

from telegraph.common.symbols import Symbol
from telegraph.learnMorse.alphabet import morse
from telegraph.learnMorse.testModes.testModeInterface import TestModeInterface


class RandomLettersMode(TestModeInterface):

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		signal.signal(signal.SIGINT, self.handleSigInt)

		self.masterList = []
		self.user = user
		self.initializeTiming(charWpm, overallWpm)

		self.chars = []
		for _ in range(numChars):
			self.chars.append(morse.popitem(False))

		self.timer = Timer(testTime, self.stopTest)

		sleep(2)
		self.running = True
		self.timer.start()
		self.startTest()

	def startTest(self):

		print("Enter what you hear:")
		print(" > ", end="")
		sys.stdout.flush()

		while self.running:

			wordLength = random.choice(range(10)) + 1
			for i in range(wordLength):
				char = random.choice(self.chars)
				self.masterList.append(char[0])

				for symbol in char[1]:
					if symbol == Symbol.DIT:
						self.playDit()
					else:
						self.playDah()
					self.playSymbolSpace()

				if i == wordLength-1:
					self.playWordSpace()
				else:
					self.playCharSpace()

			self.masterList.append(' ')

		#Remove final word space
		self.masterList.pop()

		response = input()
		master = "".join(self.masterList)
		print("   " + master)
		self.checkAnswer(response.upper(), master)


import random
import subprocess

from learnMorse.alphabet import morse
from symbols import Symbol
from threading import Timer
from time import sleep


COUNTS_PER_WORD = 50
MS_PER_MINUTE = 60000

class morseTest:

	def __init__(self, charWpm, overallWpm, numChars, testTime):

		self.masterList = []
		self.charWpm = charWpm
		self.overallWpm = overallWpm
		self.msPerCount = MS_PER_MINUTE / (COUNTS_PER_WORD * self.charWpm)

		# Equations from http://www.arrl.org/files/file/Technology/x9004008.pdf
		totalDelay = (60*self.charWpm - 37.2*self.overallWpm) / \
					 (self.charWpm * self.overallWpm)
		self.symbolSpace = 1.0 / (self.charWpm/60.0 * COUNTS_PER_WORD)
		self.charSpace = 3*totalDelay / 19 - self.symbolSpace
		self.wordSpace = 7*totalDelay / 19 - self.symbolSpace

		self.chars = []
		for x in range(numChars):
			self.chars.append(morse.popitem(0))

		sleep(2)
		self.running = True
		timer = Timer(testTime, self.stopTest)
		timer.start()
		self.startTest()

	def playDit(self):
		subprocess.call(["paplay", "learnMorse/sounds/dot-20wpm.ogg"])
		sleep(self.symbolSpace)

	def playDah(self):
		subprocess.call(["paplay", "learnMorse/sounds/dash-20wpm.ogg"])
		sleep(self.symbolSpace)

	def playCharSpace(self):
		sleep(self.charSpace)

	def playWordSpace(self):
		self.masterList.append(' ')
		sleep(self.wordSpace)

	def startTest(self):

		play = {
			Symbol.DIT: self.playDit,
			Symbol.DAH: self.playDah,
		}

		while self.running:
			wordLength = random.choice(range(10)) + 1
			for x in range(wordLength):
				char = random.choice(self.chars)
				self.masterList.append(char[0])
				for symbol in char[1]:
					play[symbol]()
				self.playCharSpace()
			self.playWordSpace()

		for char in self.masterList:
			print(char, end="")
		print()

	def stopTest(self):
		self.running = False


import difflib
import random
import subprocess
import sys
import signal

from src.learnMorse.alphabet import morse
from src.learnMorse import users
from src.symbols import Symbol
from threading import Timer
from time import sleep


COUNTS_PER_WORD = 50
MS_PER_MINUTE = 60000

class morseTest:

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		signal.signal(signal.SIGINT, self.handleSigInt)

		self.masterList = []
		self.charWpm = charWpm
		self.overallWpm = overallWpm
		self.msPerCount = MS_PER_MINUTE / (COUNTS_PER_WORD * self.charWpm)
		self.ditFile = "dot-20wpm.ogg" if charWpm == 20 else "dot-15wpm.ogg"
		self.dahFile = "dash-20wpm.ogg" if charWpm == 20 else "dash-15wpm.ogg"
		self.user = user

		# Equations from http://www.arrl.org/files/file/Technology/x9004008.pdf
		totalDelay = (60*self.charWpm - 37.2*self.overallWpm) / \
					 (self.charWpm * self.overallWpm)
		self.symbolSpace = 1.0 / (self.charWpm/60.0 * COUNTS_PER_WORD)
		self.charSpace = 3*totalDelay / 19 - self.symbolSpace
		self.wordSpace = 7*totalDelay / 19 - self.symbolSpace

		self.chars = []
		for x in range(numChars):
			self.chars.append(morse.popitem(0))

		self.timer = Timer(testTime, self.stopTest)

		sleep(2)
		self.running = True
		self.timer.start()
		self.startTest()

	def handleSigInt(self, sig, frame):
		self.timer.cancel()
		sys.exit()

	def playDit(self):
		subprocess.call(["paplay", "resources/sounds/" + self.ditFile])
		sleep(self.symbolSpace)

	def playDah(self):
		subprocess.call(["paplay", "resources/sounds/" + self.dahFile])
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

		print("Enter what you hear:")
		print(" > ", end="")
		sys.stdout.flush()

		while self.running:
			wordLength = random.choice(range(8)) + 1
			for x in range(wordLength):
				char = random.choice(self.chars)
				self.masterList.append(char[0])
				for symbol in char[1]:
					play[symbol]()
				self.playCharSpace()
			self.playWordSpace()

		#Remove final word space
		self.masterList.pop()

		response = input()
		master = "".join(self.masterList)
		print("   " + master)
		self.checkAnswer(response.upper(), master)

	def checkAnswer(self, response, master):
		diff = difflib.SequenceMatcher(None, master, response, autojunk=False)
		score = diff.ratio() * 100
		print()
		print("Score: " + str(score) + "%")
		if score >= 90:
			users.increaseCharacters(self.user)

	def stopTest(self):
		self.running = False

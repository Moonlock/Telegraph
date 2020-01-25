from subprocess import Popen
from threading import Timer
from time import sleep
import difflib
import os
import random
import signal
import subprocess
import sys

from src.learnMorse import users
from src.learnMorse.alphabet import morse
from src.symbols import Symbol


COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60

SOUND_FILES_PATH = "resources/sounds/"
DIT_FILE = SOUND_FILES_PATH + "learnMorse-dit.sox"
DAH_FILE = SOUND_FILES_PATH + "learnMorse-dah.sox"
SYMBOL_SPACE_FILE = SOUND_FILES_PATH + "learnMorse-symbol.sox"
CHAR_SPACE_FILE = SOUND_FILES_PATH + "learnMorse-char.sox"
WORD_SPACE_FILE = SOUND_FILES_PATH + "learnMorse-word.sox"
TEST_FILE = SOUND_FILES_PATH + "learnMorse-test.sox"
CREATED_FILES = [DIT_FILE, DAH_FILE, SYMBOL_SPACE_FILE, CHAR_SPACE_FILE, WORD_SPACE_FILE, TEST_FILE]


class morseTest:

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		signal.signal(signal.SIGINT, self.handleSigInt)

		self.masterList = []
		self.user = user
		self.charWpm = charWpm
		self.overallWpm = overallWpm
		timeUnit = SECONDS_PER_MINUTE / (COUNTS_PER_WORD * self.charWpm)
		self.ditLength = timeUnit
		self.dahLength = 3*timeUnit
		Popen(['sox', '-n', DIT_FILE, 'synth', str(timeUnit), 'sin', '900'])
		Popen(['sox', '-n', DAH_FILE, 'synth', str(3*timeUnit), 'sin', '900'])

		# Equations from http://www.arrl.org/files/file/Technology/x9004008.pdf
		totalDelay = (60*self.charWpm - 37.2*self.overallWpm) / \
					 (self.charWpm * self.overallWpm)
		self.symbolSpace = 1.0 / (self.charWpm/60.0 * COUNTS_PER_WORD)
		self.charSpace = 3*totalDelay / 19 - self.symbolSpace
		self.wordSpace = 7*totalDelay / 19 - self.symbolSpace

		Popen(['sox', '-n', SYMBOL_SPACE_FILE, 'trim', '0', str(self.symbolSpace)])
		Popen(['sox', '-n', CHAR_SPACE_FILE, 'trim', '0', str(3*self.charSpace)])
		Popen(['sox', '-n', WORD_SPACE_FILE, 'trim', '0', str(7*self.wordSpace)])

		self.chars = []
		for _ in range(numChars):
			self.chars.append(morse.popitem(0))

#		self.timer = Timer(testTime, self.stopTest)
		self.testTime = testTime

		sleep(2)
#		self.running = True
#		self.timer.start()
		self.startTest()

	def handleSigInt(self, sig, frame):
		self.timer.cancel()

		for file in CREATED_FILES:
			if os.path.exists(file):
				os.remove(file)

		sys.exit()

	def playDit(self):
		subprocess.call(["play", '-q', DIT_FILE])
		sleep(self.symbolSpace*2)

	def playDah(self):
		subprocess.call(["play", '-q', DAH_FILE])
		sleep(self.symbolSpace*4)

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

		filename = "{}.sox".format(SOUND_FILES_PATH + "test")
		command = ['sox']
		command.extend(fileList)
		command.append(filename)
		Popen(command)
		Popen(['play', '-q', filename])

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

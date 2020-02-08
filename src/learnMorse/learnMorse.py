from subprocess import Popen, call
from time import sleep
import difflib
import glob
import os
import random
import signal
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
		Popen(['sox', '-n', CHAR_SPACE_FILE, 'trim', '0', str(self.charSpace)])
		Popen(['sox', '-n', WORD_SPACE_FILE, 'trim', '0', str(self.wordSpace)])

		self.chars = []
		for _ in range(numChars):
			self.chars.append(morse.popitem(0))

		self.testTime = testTime

		sleep(2)
		self.startTest()

	def handleSigInt(self, sig, frame):
		self.deleteFiles()
		sys.exit()

	def deleteFiles(self):
		files = glob.glob(SOUND_FILES_PATH + "learnMorse-*.sox")
		for file in files:
			try:
				os.remove(file)
			except:
				print("Failed to delete " + file)

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

		testFile = self.createFile(fileList)
		Popen(['play', '-q', testFile])
		self.deleteFiles()

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

	def createFile(self, fileList):
		partialFile = ""
		for i in range((len(fileList) + 999) // 1000):
			start = i * 1000
			end = (i+1) * 1000

			oldPartialFile = partialFile
			partialFile = SOUND_FILES_PATH + "learnMorse-{}.sox".format(i)
			files = fileList[start:end]

			command = ['sox']
			if oldPartialFile:
				command.append(oldPartialFile)
			command.extend(files)
			command.append(partialFile)
			call(command)

		return partialFile

	def stopTest(self):
		self.running = False

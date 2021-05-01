import difflib

import numpy

from telegraph.learnMorse import users
import pygame.mixer
import pygame.time


COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60

SAMPLE_RATE = 44100
FREQUENCY = 800


class TestModeInterface:

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		pass

	def handleSigInt(self, sig, frame):
		self.timer.cancel()
		self.running = False

	def stopTest(self):
		self.running = False

	def checkAnswer(self, response, master, updateUser=False):
		diff = difflib.SequenceMatcher(None, master, response, autojunk=False)
		score = diff.ratio() * 100
		print()
		print("Score: " + "{:.2f}".format(score) + "%")

		if updateUser and score >= 90:
			users.increaseCharacters(self.user)

	def playDit(self):
		samples = numpy.arange(SAMPLE_RATE * self.ditLength)
		buffer = numpy.sin(2*numpy.pi * samples * FREQUENCY / SAMPLE_RATE).astype(numpy.float32)
		sound = pygame.mixer.Sound(buffer)
		sound.play()

		pygame.time.delay(int(self.ditLength * 1000))

	def playDah(self):
		samples = numpy.arange(SAMPLE_RATE * self.dahLength)
		buffer = numpy.sin(2*numpy.pi * samples * FREQUENCY / SAMPLE_RATE).astype(numpy.float32)
		sound = pygame.mixer.Sound(buffer)
		sound.play()

		pygame.time.delay(int(self.dahLength * 1000))

	def playSymbolSpace(self):
		pygame.time.delay(int(self.symbolSpace * 1000))

	def playCharSpace(self):
		pygame.time.delay(int(self.charSpace * 1000))

	def playWordSpace(self):
		pygame.time.delay(int(self.wordSpace * 1000))

	def initializeTiming(self, charWpm, overallWpm):
		pygame.mixer.init()

		timeUnit = SECONDS_PER_MINUTE / (COUNTS_PER_WORD * charWpm)
		self.ditLength = timeUnit
		self.dahLength = 3*timeUnit

		# Equations from http://www.arrl.org/files/file/Technology/x9004008.pdf
		totalDelay = (60*charWpm - 37.2*overallWpm) / \
					 (charWpm * overallWpm)
		self.symbolSpace = timeUnit
		# Subtract symbolSpace from other spaces to account for symbol space being played after every dit/dah.
		self.charSpace = 3*totalDelay / 19 - self.symbolSpace
		self.wordSpace = 7*totalDelay / 19 - self.symbolSpace

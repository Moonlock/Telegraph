from enum import Enum
from threading import Timer
import random
import signal

from telegraph.common.commonFunctions import debug
from telegraph.common.symbols import Symbol
from telegraph.learnMorse.alphabet import morse
import pigpio


COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60

KEY_CHANNEL = 4
TICK_ROLLOVER = 4294967296

INIT_MESSAGE_TIME_UNITS = 15


class Mode(Enum):
	INIT = 0
	TEST = 1

class SendMode:

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		signal.signal(signal.SIGINT, self.handleSigInt)

		self.user = user

		self.chars = []
		for _ in range(numChars):
			self.chars.append(morse.popitem(0))

		self.pi = pigpio.pi()
		self.lastTick = 0
		self.initTimings = []

		self.mode = Mode.INIT
		self.callbacks = {Mode.INIT: self.initKeyEvent,
						Mode.TEST: self.testKeyEvent}

		self.timer = Timer(testTime, self.stopTest)

		self.running = True
		self.initialize()


	def handleSigInt(self, sig, frame):
		self.timer.cancel()
		self.running = False

	def stopTest(self):
		self.running = False

	def keyCallback(self, channel, level, tick):
		self.callbacks[self.mode](level, tick)

	def initKeyEvent(self, level, tick):
		elapsedTime = tick - self.lastTick
		if elapsedTime < 0:
			elapsedTime += TICK_ROLLOVER

		event = "Release" if level == 0 else "Press"
		debug("{}: {}".format(event, int(elapsedTime/1000)))
		self.initTimings.append(elapsedTime)
		if len(self.initTimings) == 10:
			self.checkStart()

		self.lastTick = tick

	def testKeyEvent(self, level, tick):
		elapsedTime = tick - self.lastTick
		if elapsedTime < 0:
			elapsedTime += TICK_ROLLOVER

		if level == 0:
			debug("Release: " + str(int(elapsedTime/1000)))
			self.handlePress(elapsedTime)
		else:
			debug("Press: " + str(int(elapsedTime/1000)))
			self.handleRelease(elapsedTime)

		self.lastTick = tick

	def handlePress(self, releaseTimeUsec):
		if self.userSymbols:
			if releaseTimeUsec > 5*self.timeUnitUsec:
				self.userSymbols.append(Symbol.WORD_SPACE)
			elif releaseTimeUsec >= 2*self.timeUnitUsec:
				self.userSymbols.append(Symbol.CHAR_SPACE)

	def handleRelease(self, pressTimeUsec):
		if pressTimeUsec < 2*self.timeUnitUsec:
			self.userSymbols.append(Symbol.DIT)
		else:
			self.userSymbols.append(Symbol.DAH)

	def checkStart(self):
		dahs = self.initTimings[1::4]
		dits = self.initTimings[3::4]
		spaces = self.initTimings[2::2]

		if min(dahs) < 2*max(dits + spaces):
			self.initTimings.pop(0)
			return

		self.timeUnitUsec = sum(dits + dahs + spaces) / INIT_MESSAGE_TIME_UNITS
		self.initTimings.clear()
		debug("Starting with timeunit " + str(int(self.timeUnitUsec/1000)) + "ms")
		self.pi.event_trigger(KEY_CHANNEL)

	def initialize(self):
		self.pi.set_mode(KEY_CHANNEL, pigpio.INPUT)
		self.pi.callback(KEY_CHANNEL, pigpio.EITHER_EDGE, self.keyCallback)
		self.pi.set_glitch_filter(KEY_CHANNEL, 10 * 1000)

		debug("Waiting for init.  (dah-dit-dah-dit-dah)")
		self.pi.wait_for_event(KEY_CHANNEL, 600)
		debug("Received init")
		self.timer.start()
		self.startTest()

	def startTest(self):
		self.mode = Mode.TEST
		timeout = 5*self.timeUnitUsec / 1000000

		correct = 0
		incorrect = 0
		while self.running:
			self.userSymbols = []
			sending = True
			char = random.choice(self.chars)
			print(char[0])

			while not self.userSymbols or sending:
				sending = self.pi.wait_for_edge(KEY_CHANNEL, pigpio.EITHER_EDGE, timeout)

			if self.userSymbols == char[1]:
				correct += 1
			else:
				print("Received: {}".format(self.userSymbols))
				incorrect += 1

		print("Correct: {}".format(correct))
		print("Incorrect: {}".format(incorrect))
		print("Score: {}".format(correct - incorrect))


















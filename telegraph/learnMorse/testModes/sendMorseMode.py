from threading import Timer
import random
import signal

from telegraph.common.clientMode import ClientMode
from telegraph.common.commonFunctions import debug
from telegraph.common.symbols import Symbol
from telegraph.learnMorse.alphabet import morse
from telegraph.learnMorse.testModes.testModeInterface import TestModeInterface
import pigpio


USEC_PER_MSEC = 1000

KEY_CHANNEL = 4
TICK_ROLLOVER = 4294967296

INIT_MESSAGE_TIME_UNITS = 15


class SendMode(TestModeInterface):

	def __init__(self, charWpm, overallWpm, numChars, testTime, user):
		signal.signal(signal.SIGINT, self.handleSigIntWithTimer)

		self.user = user

		self.chars = []
		for _ in range(numChars):
			self.chars.append(morse.popitem(0))

		self.pi = pigpio.pi()
		self.lastTick = 0
		self.initTimings = []

		self.mode = ClientMode.INIT
		self.callbacks = {ClientMode.INIT: self.initKeyEvent,
						ClientMode.MAIN: self.testKeyEvent}

		self.timer = Timer(testTime, self.stopTest)

		self.running = True
		self.initialize()

	def stopTest(self):
		self.running = False

	def keyCallback(self, channel, level, tick):
		elapsedTime = tick - self.lastTick
		if elapsedTime < 0:
			elapsedTime += TICK_ROLLOVER

		event = "Release" if level == 0 else "Press"
		debug("{}: {}".format(event, int(elapsedTime/USEC_PER_MSEC)))

		self.lastTick = tick
		self.callbacks[self.mode](level, elapsedTime)

	def initKeyEvent(self, level, elapsedTime):
		self.initTimings.append(elapsedTime)
		if len(self.initTimings) == 10:
			self.checkStart()

	def testKeyEvent(self, level, elapsedTime):
		if level == 0:
			self.handlePress(elapsedTime)
		else:
			self.handleRelease(elapsedTime)

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
		print("Starting with timeunit " + str(int(self.timeUnitUsec/USEC_PER_MSEC)) + "ms")
		self.pi.event_trigger(KEY_CHANNEL)

	def initialize(self):
		self.pi.set_mode(KEY_CHANNEL, pigpio.INPUT)
		self.pi.callback(KEY_CHANNEL, pigpio.EITHER_EDGE, self.keyCallback)
		self.pi.set_glitch_filter(KEY_CHANNEL, 10 * USEC_PER_MSEC)

		print("Waiting for init.  (-.-.-)")
		self.pi.wait_for_event(KEY_CHANNEL, 600)
		print("Received init")
		self.timer.start()
		self.startTest()

	def startTest(self):
		self.mode = ClientMode.MAIN
		timeoutSec = 5*self.timeUnitUsec / 1000000

		correct = 0
		incorrect = 0
		while self.running:
			self.userSymbols = []
			sending = True
			char = random.choice(self.chars)
			print(char[0])

			while self.running and (not self.userSymbols or sending):
				sending = self.pi.wait_for_edge(KEY_CHANNEL, pigpio.EITHER_EDGE, timeoutSec)

			if self.userSymbols == char[1]:
				correct += 1
			else:
				print("Received: {}".format(self.userSymbols))
				incorrect += 1

		print("Correct: {}".format(correct))
		print("Incorrect: {}".format(incorrect))
		print("Score: {}".format(correct - incorrect))


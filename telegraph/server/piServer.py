from threading import Lock, Thread
from time import sleep

from telegraph.common.commonFunctions import debug
from telegraph.common.symbols import Symbol
from telegraph.server.server import Server
import pigpio


CHANNEL = 18
FREQUENCY = 900

class PiServer(Server):

	def __init__(self, port, wpm, listener, killed, sendInProgress):
		super().__init__(port, wpm, listener, killed, sendInProgress)

		self.messages = []
		self.messagePlayLock = Lock()

		self.pi = pigpio.pi()
		self.pi.set_mode(CHANNEL, pigpio.OUTPUT)

		self.play = {Symbol.DIT: self.playDit,
					Symbol.DAH: self.playDah,
					Symbol.CHAR_SPACE: self.playCharSpace,
					Symbol.WORD_SPACE: self.playWordSpace}

		self.start()

	def cleanUp(self):
		self.pi.stop()

	def checkUnplayedMessages(self):
		if self.unplayedMessages and not self.sendInProgress.isSet():
			played = self.playMessage(message=self.unplayedMessages[0])
			if played:
				self.unplayedMessages.pop(0)

	def handleMessage(self, msg):
		parsedMsg = self.parseMessage(msg)
		self.messages.append(parsedMsg)

		self.listener.updateMessageIndicator(len(self.messages))

		if self.sendInProgress.isSet():
			debug("Send in progress, delaying message.")
			self.unplayedMessages.append(parsedMsg)
		elif not self.playMessage(message=parsedMsg):
			self.unplayedMessages.append(parsedMsg)

	def playMessage(self, channel=None, message=None):

		def innerPlayMessage(message):
			prevIsChar = False

			for symbol in message:
				isChar = symbol.isChar()
				if isChar and prevIsChar:
					self.playSymbolSpace()

				self.play[symbol]()
				prevIsChar = isChar

			self.messagePlayLock.release()

		if message is None:
			if not self.messages:
				debug("No message to play.")
				return False
			message = self.messages[0]

		if not self.messagePlayLock.acquire(False):
			debug("Already playing a message.")
			return False

		playThread = Thread(target=innerPlayMessage, args=([message]))
		playThread.start()

		return True

	def playDit(self):
		self.pi.hardware_PWM(CHANNEL, FREQUENCY, 500000)
		sleep(self.timeUnit)
		self.pi.hardware_PWM(CHANNEL, FREQUENCY, 0)

	def playDah(self):
		self.pi.hardware_PWM(CHANNEL, FREQUENCY, 500000)
		sleep(self.timeUnit * 3)
		self.pi.hardware_PWM(CHANNEL, FREQUENCY, 0)

	def playSymbolSpace(self):
		sleep(self.timeUnit)

	def playCharSpace(self):
		sleep(self.timeUnit*3)

	def playWordSpace(self):
		sleep(self.timeUnit*7)

	def deleteMessage(self, channel=None):
		debug("delete message.")
		if self.messages:
			self.messages.pop(0)
			self.listener.updateMessageIndicator(len(self.messages))


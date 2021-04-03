from math import ceil
import socket

from telegraph.client.destinationConfig import DestinationConfig
from telegraph.common.commonFunctions import debug
from telegraph.common.symbols import Symbol
import termios


INIT_MESSAGE_TIME_UNITS = 15
INIT_MESSAGE_SYMBOL_LENGTH = 6	# Includes word space following init message
END_MESSAGE = [Symbol.DIT, Symbol.DAH, Symbol.DIT, Symbol.DAH, Symbol.DIT]

class Client:

	def __init__(self, multiDest, serv, servPort, listener, killed, sendInProgress, isTest=False):
		self.multiDest = multiDest
		self.waitingForDest = multiDest
		if multiDest:
			self.dests = None
		else:
			self.dests = [(serv, servPort)]

		self.message = []
		self.initTimings = []
		self.timeUnitUsec = 0
		self.pressed = False

		self.destConfig = DestinationConfig(self.callSignError)

		self.pressCallback = self.initHandlePress
		self.releaseCallback = self.initHandleRelease
		self.listener = listener
		self.listener.resetClientCallback(self.initHandlePress, self.initHandleRelease)

		self.sendInProgress = sendInProgress

		if not isTest:
			killed.wait()
		self.listener.cleanUp()

	def initHandlePress(self, releaseTimeUsec):
		self.initTimings.append(releaseTimeUsec)
		if len(self.initTimings) == 10:
			self.checkStart()

	def initHandleRelease(self, pressTimeUsec):
		self.initTimings.append(pressTimeUsec)
		if len(self.initTimings) == 10:
			self.checkStart()

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
		self.startMessage()


	def startMessage(self):
		self.listener.startMessage()
		self.sendInProgress.set()
		self.addInitialization()
		self.listener.resetClientCallback(self.handlePress, self.handleRelease)

	def addInitialization(self):
		self.message.append(Symbol.DAH)
		self.message.append(Symbol.DIT)
		self.message.append(Symbol.DAH)
		self.message.append(Symbol.DIT)
		self.message.append(Symbol.DAH)

	def handlePress(self, releaseTimeUsec):
		if releaseTimeUsec > 5*self.timeUnitUsec:
			self.message.append(Symbol.WORD_SPACE)
			if self.waitingForDest and len(self.message) > INIT_MESSAGE_SYMBOL_LENGTH:
				self.dests = self.parseDestination()
				return

		elif releaseTimeUsec >= 2*self.timeUnitUsec:
			self.message.append(Symbol.CHAR_SPACE)

		self.checkFinish()

	def handleRelease(self, pressTimeUsec):
		if pressTimeUsec < 2*self.timeUnitUsec:
			self.message.append(Symbol.DIT)
		else:
			self.message.append(Symbol.DAH)
		self.checkFinish()

	def parseDestination(self):
		destBounds = [i for i, e in enumerate(self.message) if e == Symbol.WORD_SPACE]

		if len(destBounds) != 2:
			self.callSignError("Error parsing call sign")
			return

		start = destBounds[0] + 1
		end = destBounds[1]
		sign = self.message[start : end]

		dest = self.destConfig.createDestination(sign)
		if dest is None:
			return []

		debug("Sending to " + dest.toString() + ".")

		self.waitingForDest = False
		return dest.getEndpoints()

	def callSignError(self, message):
		self.listener.error(message + ": Canceling message.")
		self.sendInProgress.clear()
		self.message.clear()
		self.listener.resetClientCallback(self.initHandlePress, self.initHandleRelease)

	def checkFinish(self):
		if self.message[-5:] == END_MESSAGE:
			self.sendMessage()
			if self.multiDest:
				self.waitingForDest = True
				self.dests = None

			self.sendInProgress.clear()
			self.listener.resetClientCallback(self.initHandlePress, self.initHandleRelease)

	def sendMessage(self):
		for dest in self.dests:
			sock = self.connectToServer(dest[0], dest[1])
			if sock is not None:
				self.sendToServer(sock, self.createMessage())
				sock.close()

	def connectToServer(self, server, port):
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.connect((server, int(port)))
			return sock
		except socket.error as e:
			self.listener.error("Failed to create socket.  {}: {}".format(e.errno, e.strerror))
			return None

	def createMessage(self):
		messageData = 0
		messageLen = len(self.message)
		for i in range(messageLen):
			symbol = self.message.pop()
			messageData |= (symbol << i*2)
		return messageData.to_bytes(ceil(messageLen/4), byteorder='big')

	def sendToServer(self, sock, message):
		try:
			sock.sendall(message)
			self.listener.sendSuccess()
		except socket.error as e:
			self.listener.error("Failed to send message.  {}: {}".format(e.errno, e.strerror))

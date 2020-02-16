from math import ceil
from time import time
import socket
import sys

from pynput import keyboard

from src.commonFunctions import debug, fatal
from src.symbols import Symbol
from src.telegraph.destinationConfig import DestinationConfig
import termios


#from RPi import GPIO
KEY_CHANNEL = 4
INIT_MESSAGE_TIME_UNITS = 15
INIT_MESSAGE_SYMBOL_LENGTH = 6	# Includes word space following init message
END_MESSAGE = [Symbol.DIT, Symbol.DAH, Symbol.DIT, Symbol.DAH, Symbol.DIT]

class Client:

	def __init__(self, multiDest, serv, servPort, listener, killed, isTest=False):
		self.multiDest = multiDest
		self.waitingForDest = multiDest
		if multiDest:
			self.dests = None
		else:
			self.dests = [(serv, servPort)]

		self.message = []
		self.initTimings = []
		self.lastPress = 0
		self.lastRelease = 0
		self.timeUnit = 0
		self.pressed = False

		self.destConfig = DestinationConfig(self.callSignError)

		self.callback = self.initCallback
		self.pressCallback = self.initHandlePress
		self.releaseCallback = self.initHandleRelease
#		self.setUpCallback()
		self.listener = listener
		self.listener.resetClientCallback(self.initCallback, self.initHandlePress, self.initHandleRelease)

		if not isTest:
			killed.wait()
		self.listener.cleanUp()

	def setUpCallback(self):
		def innerCallback(channel):
			self.callback(channel)
		def innerPressCallback(key):
			if not self.pressed:
				self.pressed = True
				self.pressCallback()
			if key == keyboard.Key.esc:
				return False
		def innerReleaseCallback(key):
			self.pressed = False
			self.releaseCallback()

		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		new = termios.tcgetattr(fd)
		new[3] = new[3] & ~termios.ECHO
		try:
			termios.tcsetattr(fd, termios.TCSADRAIN, new)
			with keyboard.Listener(on_press=innerPressCallback, on_release=innerReleaseCallback) as listener:
				listener.join()
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


#		GPIO.setmode(GPIO.BCM)
#		GPIO.setup(KEY_CHANNEL, GPIO.IN)
#		GPIO.add_event_detect(KEY_CHANNEL, GPIO.BOTH, callback=innerCallback, bouncetime=20)

	def timePress(self):
		self.lastRelease = time()
		pressTime = (self.lastRelease - self.lastPress) * 1000
		debug("Press: " + str(int(pressTime)))
		return pressTime

	def timeRelease(self):
		self.lastPress = time()
		releaseTime = (self.lastPress - self.lastRelease) * 1000
		debug("Release: " + str(int(releaseTime)))
		return releaseTime

	def initCallback(self, channel):
#		if GPIO.input(channel) == 0:
#			self.initHandlePress()
#		else:
#			self.initHandleRelease()
		pass

	def initHandlePress(self):
		releaseTimeMs = self.timeRelease()

		self.initTimings.append(releaseTimeMs)
		if len(self.initTimings) == 10:
			self.checkStart()

	def initHandleRelease(self):
		pressTimeMs = self.timePress()

		self.initTimings.append(pressTimeMs)
		if len(self.initTimings) == 10:
			self.checkStart()

	def checkStart(self):
		dahs = self.initTimings[1::4]
		dits = self.initTimings[3::4]
		spaces = self.initTimings[2::2]

		if min(dahs) < 2*max(dits + spaces):
			self.initTimings.pop(0)
			return

		self.timeUnit = sum(dits + dahs + spaces) / INIT_MESSAGE_TIME_UNITS
		self.initTimings.clear()
		debug("Starting with timeunit " + str(self.timeUnit))
		self.startMessage()


	def startMessage(self):
		print("Start")
		self.addInitialization()
		self.listener.resetClientCallback(self.messageCallback, self.handlePress, self.handleRelease)
#		self.callback = self.messageCallback
#		self.pressCallback = self.handlePress
#		self.releaseCallback = self.handleRelease

	def addInitialization(self):
		self.message.append(Symbol.DAH)
		self.message.append(Symbol.DIT)
		self.message.append(Symbol.DAH)
		self.message.append(Symbol.DIT)
		self.message.append(Symbol.DAH)

	def messageCallback(self, channel):
#		if GPIO.input(channel) == 0:
#			self.handlePress()
#		else:
#			self.handleRelease()
		pass

	def handlePress(self):
		releaseTimeMs = self.timeRelease()

		if releaseTimeMs > 5*self.timeUnit:
			self.message.append(Symbol.WORD_SPACE)
			if self.waitingForDest and len(self.message) > INIT_MESSAGE_SYMBOL_LENGTH:
				self.dests = self.parseDestination()
				return

		elif releaseTimeMs >= 2*self.timeUnit:
			self.message.append(Symbol.CHAR_SPACE)

		self.checkFinish()

	def handleRelease(self):
		pressTimeMs = self.timePress()

		if pressTimeMs < 2*self.timeUnit:
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
		debug(message + ": Canceling message.")
		self.message.clear()
		self.listener.resetClientCallback(self.initCallback, self.initHandlePress, self.initHandleRelease)
#		self.callback = self.initCallback
#		self.pressCallback = self.initHandlePress
#		self.releaseCallback = self.initHandleRelease

	def checkFinish(self):
		if self.message[-5:] == END_MESSAGE:
			debug("Sending message.")
			self.sendMessage()
			if self.multiDest:
				self.waitingForDest = True
				self.dests = None

			self.listener.resetClientCallback(self.initCallback, self.initHandlePress, self.initHandleRelease)
#			self.callback = self.initCallback
#			self.pressCallback = self.initHandlePress
#			self.releaseCallback = self.initHandleRelease

	def sendMessage(self):
		for dest in self.dests:
			sock = self.connectToServer(dest[0], dest[1])
			self.sendToServer(sock, self.createMessage())
			sock.close()

	def connectToServer(self, server, port):
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.connect((server, int(port)))
			return sock
		except socket.error as e:
			fatal("Failed to create socket.  {}: {}".format(e.errno, e.strerror))

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
		except socket.error as e:
			fatal("Failed to send message.  {}: {}".format(e.errno, e.strerror))

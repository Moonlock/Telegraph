import socket
import sys

from math import ceil
from RPi import GPIO
from time import time, sleep

from src.symbols import Symbol

DEBUG = False

CHANNEL = 4
INIT_MESSAGE_TIME_UNITS = 15
END_MESSAGE = [Symbol.DIT, Symbol.DAH, Symbol.DIT, Symbol.DAH, Symbol.DIT]

class Client:

	def __init__(self, serv, servPort, killed):
		self.server = serv
		self.port = servPort

		self.message = []
		self.initTimings = []
		self.lastPress = 0
		self.lastRelease = 0
		self.timeUnit = 0

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(CHANNEL, GPIO.IN)
		self.resetCallbacks(self.initCallback)

		killed.wait()
		GPIO.cleanup()

	def debug(self, message):
		if DEBUG:
			print(message)

	def timePress(self):
		now = time()

		self.lastRelease = now
		self.debug("Press: " + str(int((now - self.lastPress) * 1000)))
		return (now - self.lastPress) * 1000

	def timeRelease(self):
		now = time()

		self.lastPress = now
		self.debug("Release: " + str(int((now - self.lastRelease) * 1000)))
		return (now - self.lastRelease) * 1000


	def initCallback(self, channel):
		# Hacky way to wait until bouncing stops
		# until I get a capacitor.
		sleep(0.040)

		if GPIO.input(channel) == 1:
			self.initHandlePress()
		else:
			self.initHandleRelease()

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
		self.initTimings.clear()

		if min(dahs) < 2*max(dits + spaces):
			self.debug("Init sequence incorrect.")
			return

		self.timeUnit = sum(dits + dahs + spaces) / INIT_MESSAGE_TIME_UNITS
		self.debug("Starting")
		self.startMessage()


	def startMessage(self):
		self.addInitialization()
		self.resetCallbacks(self.messageCallback)

	def addInitialization(self):
		self.message.append(Symbol.DAH)
		self.message.append(Symbol.DIT)
		self.message.append(Symbol.DAH)
		self.message.append(Symbol.DIT)
		self.message.append(Symbol.DAH)
		self.message.append(Symbol.WORD_SPACE)

	def messageCallback(self, channel):
		# Hacky way to wait until bouncing stops
		# until I get a capacitor.
		sleep(0.040)

		if GPIO.input(channel) == 1:
			self.handlePress()
		else:
			self.handleRelease()

	def handlePress(self):
		releaseTimeMs = self.timeRelease()

		if releaseTimeMs > 5*self.timeUnit:
			self.message.append(Symbol.WORD_SPACE)
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

	def checkFinish(self):
		if self.message[-5:] == END_MESSAGE:
			self.debug("Sending message.")
			self.sendMessage()
			self.resetCallbacks(self.initCallback)

	def sendMessage(self):
		self.connectToServer()
		self.sendToServer(self.createMessage())
		self.s.close()

	def sendToServer(self, message):
		try:
			self.s.sendall(message)
		except socket.error as e:
			print("Failed to send message.  {}: {}".format(e.errno, e.strerror))
			sys.exit()

	def createMessage(self):
		messageData = 0
		messageLen = len(self.message)
		for i in range(messageLen):
			symbol = self.message.pop()
			messageData |= (symbol << i*2)
		return messageData.to_bytes(ceil(messageLen/4), byteorder='big')

	def resetCallbacks(self, callback):
		GPIO.remove_event_detect(CHANNEL)
		GPIO.add_event_detect(CHANNEL, GPIO.BOTH, callback=callback, bouncetime=50)

	def connectToServer(self):
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.s.connect((self.server, int(self.port)))
		except socket.error as e:
			print("Failed to create socket.  {}: {}".format(e.errno, e.strerror))
			sys.exit()

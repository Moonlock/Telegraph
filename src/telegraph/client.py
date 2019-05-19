import configparser
import socket
import sys

from math import ceil
from RPi import GPIO
from time import time, sleep

from src.symbols import Symbol
import setup

CHANNEL = 4
INIT_MESSAGE_TIME_UNITS = 15
END_MESSAGE = [Symbol.DIT, Symbol.DAH, Symbol.DIT, Symbol.DAH, Symbol.DIT]

class Client:

	def __init__(self, multiDest, serv, servPort, killed, debug):
		self.dbgEnabled = debug

		self.multiDest = multiDest
		self.waitingForDest = multiDest
		if multiDest:
			self.dests = None
		else:
			self.dests = (serv, servPort)

		self.message = []
		self.initTimings = []
		self.lastPress = 0
		self.lastRelease = 0
		self.timeUnit = 0

		self.destinations = configparser.ConfigParser()
		self.destinations.read(setup.DEST_FILE)

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		self.resetCallbacks(self.initCallback)

		killed.wait()

	def debug(self, message):
		if self.dbgEnabled:
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

		if min(dahs) < 2*max(dits + spaces):
			self.initTimings.pop(0)
			return

		self.timeUnit = sum(dits + dahs + spaces) / INIT_MESSAGE_TIME_UNITS
		self.initTimings.clear()
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
			if self.waitingForDest:
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

		if len(destBounds != 2):
			self.callSignError("Error parsing call sign")
			return

		start = destBounds[0] + 1
		end = destBounds[1]
		sign = self.message[start : end]

		dests = self.getDestsFromSign(sign)
		if not dests:
			self.callSignError("Call sign not found")
			return

		self.waitingForDest = False
		return dests

	def getDestsFromSign(self, sign):
		signString = "".join([str(int(symbol)) for symbol in sign])
		if not self.destinations.has_section(signString):
			return None

		config = self.destinations[signString]
		dests = []
		if config.getboolean("Group"):
			memberList = []
			for member in config["Members"]:
				memberConfig = self.destinations[member]
				memberList.append(memberConfig["Name"])
				dests.append((memberConfig["Address"], memberConfig["Port"]))
			self.debug("Sending to " + config["Name"] + ": " + ", ".join(memberList) + ".")
		else:
			self.debug("Sending to " + config["Name"] + ".")
			dests.append((config["Address"], config["Port"]))

		return dests

	def callSignError(self, message):
		self.debug(message + ": Canceling message.")
		self.resetCallbacks(self.initCallback)

	def checkFinish(self):
		if self.message[-5:] == END_MESSAGE:
			self.debug("Sending message.")
			self.sendMessage()
			if self.multiDest:
				self.waitingForDest = True
				self.dests = None

			self.resetCallbacks(self.initCallback)

	def sendMessage(self):
		for dest in self.dests:
			sock = self.connectToServer(dest[0], dest[1])
			self.sendToServer(sock, self.createMessage())
			sock.close()

	def sendToServer(self, sock, message):
		try:
			sock.sendall(message)
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

	def connectToServer(self, server, port):
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.connect((server, int(port)))
			return sock
		except socket.error as e:
			print("Failed to create socket.  {}: {}".format(e.errno, e.strerror))
			sys.exit()

import signal
import socket
import sys

from math import ceil
from RPi import GPIO
from time import time, sleep

from symbols import Symbol

CHANNEL = 4
INIT_MESSAGE_TIME_UNITS = 15
END_MESSAGE = [Symbol.DIT, Symbol.DAH, Symbol.DIT, Symbol.DAH, Symbol.DIT]

SERVER = 'localhost'
PORT = 8000

message = []
initTimings = []
lastPress = 0
lastRelease = 0
timeUnit = 0

def handleSigInt(sig, frame):
	GPIO.cleanup()

def timePress():
	now = time()

	global lastRelease
	lastRelease = now
	return (now - lastPress) * 1000

def timeRelease():
	now = time()

	global lastPress
	lastPress = now
	return (now - lastRelease) * 1000


def initCallback(channel):
	# Hacky way to wait until bouncing stops
	# until I get a capacitor.
	sleep(0.040)

	if GPIO.input(channel) == 1:
		initHandlePress()
	else:
		initHandleRelease()

def initHandlePress():
	releaseTimeMs = timeRelease()

	initTimings.append(releaseTimeMs)
	if len(initTimings) == 10:
		checkStart()

def initHandleRelease():
	pressTimeMs = timePress()

	initTimings.append(pressTimeMs)
	if len(initTimings) == 10:
		checkStart()

def checkStart():
	dahs = initTimings[1::4]
	dits = initTimings[3::4]
	spaces = initTimings[2::2]
	initTimings.clear()

	if min(dahs) < 2*max(dits + spaces):
		return

	global timeUnit
	timeUnit = sum(dits + dahs + spaces) / INIT_MESSAGE_TIME_UNITS
	startMessage()


def startMessage():
	addInitialization()
	resetCallbacks(messageCallback)

def addInitialization():
	message.append(Symbol.DAH)
	message.append(Symbol.DIT)
	message.append(Symbol.DAH)
	message.append(Symbol.DIT)
	message.append(Symbol.DAH)
	message.append(Symbol.WORD_SPACE)

def messageCallback(channel):
	# Hacky way to wait until bouncing stops
	# until I get a capacitor.
	sleep(0.040)

	if GPIO.input(channel) == 1:
		handlePress()
	else:
		handleRelease()

def handlePress():
	releaseTimeMs = timeRelease()

	if releaseTimeMs > 5*timeUnit:
		message.append(Symbol.WORD_SPACE)
	elif releaseTimeMs >= 2*timeUnit:
		message.append(Symbol.CHAR_SPACE)
	checkFinish()

def handleRelease():
	pressTimeMs = timePress()

	if pressTimeMs < 2*timeUnit:
		message.append(Symbol.DIT)
	else:
		message.append(Symbol.DAH)
	checkFinish()

def checkFinish():
	if message[-5:] == END_MESSAGE:
		sendMessage()
		resetCallbacks(initCallback)

def sendMessage():
	connectToServer()
	sendToServer(createMessage())
	s.close()

def sendToServer(message):
	try:
		s.sendall(message)
	except socket.error as e:
		print("Failed to send message.  {}: {}".format(e.errno, e.strerror))
		sys.exit()

def createMessage():
	messageData = 0
	messageLen = len(message)
	for i in range(messageLen):
		symbol = message.pop()
		messageData |= (symbol << i*2)
	return messageData.to_bytes(ceil(messageLen/4), byteorder='big')

def resetCallbacks(callback):
	GPIO.remove_event_detect(CHANNEL)
	GPIO.add_event_detect(CHANNEL, GPIO.BOTH, callback=callback, bouncetime=50)

def connectToServer():
	try:
		global s
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.connect((SERVER, int(PORT)))
	except socket.error as e:
		print("Failed to create socket.  {}: {}".format(e.errno, e.strerror))
		sys.exit()

def run():
	signal.signal(signal.SIGINT, handleSigInt)

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(CHANNEL, GPIO.IN)
	resetCallbacks(initCallback)

	signal.pause()

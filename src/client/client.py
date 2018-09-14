from RPi import GPIO
from time import time

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

	if min(dahs) < 2*max(dits + spaces):
		initTimings.clear()
		return

	global timeUnit
	timeUnit = sum(dits + dahs + spaces) / INIT_MESSAGE_TIME_UNITS
	startMessage()


def startMessage():
	addInitialization()
	resetCallbacks(handlePress, handleRelease)

def addInitialization():
	message.append(Symbol.DAH)
	message.append(Symbol.DIT)
	message.append(Symbol.DAH)
	message.append(Symbol.DIT)
	message.append(Symbol.DAH)
	message.append(Symbol.WORD_SPACE)

def handlePress():
	releaseTimeMs = timeRelease()

	if pressTimeMs > 5*timeUnit:
		message.append(Symbol.WORD_SPACE)
	elif pressTimeMs >= 2*timeUnit:
		message.append(Symbol.CHAR_SPACE)

def handleRelease():
	pressTimeMs = timePress()

	if pressTimeMs < 2*timeUnit:
		message.append(Symbol.DIT)
	else:
		message.append(Symbol.DAH)

def checkFinish():
	if message[-5:] == END_MESSAGE:
		sendMessage()
		message.clear()
		resetCallbacks(initHandlePress, initHandleRelease)

def sendMessage():
	try:
		s.sendall(message)
	except socket.error as e:
		print("Failed to send message.  {}: {}".format(e.errno, e.strerror))
		sys.exit()

def resetCallbacks(pressCb, releaseCb):
	GPIO.remove_event_detect(PIN_NUM)
	GPIO.add_event_detect(PIN_NUM, GPIO.RISING, callback=pressCb, bouncetime=40)
	GPIO.add_event_detect(PIN_NUM, GPIO.RISING, callback=releaseCb, bouncetime=40)

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
	connectToServer()

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PIN_NUM, GPIO.IN)
	resetCallbacks(initHandlePress, initHandleRelease)

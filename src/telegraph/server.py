from os import remove
from subprocess import Popen
import socket

#from RPi import GPIO
from src.commonFunctions import debug, fatal
from src.symbols import Symbol


LED_CHANNEL = 16
PLAY_BUTTON_CHANNEL = 20
DELETE_BUTTON_CHANNEL = 21
COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60

SOUND_FILES_PATH = "resources/sounds/"
DIT_FILE = SOUND_FILES_PATH + "dit.sox"
DAH_FILE = SOUND_FILES_PATH + "dah.sox"
SYMBOL_SPACE_FILE = SOUND_FILES_PATH + "symbol_space.sox"
CHAR_SPACE_FILE = SOUND_FILES_PATH + "char_space.sox"
WORD_SPACE_FILE = SOUND_FILES_PATH + "word_space.sox"
INIT_SPACE_FILE = SOUND_FILES_PATH + "init_space.sox"

class Server:

	def __init__(self, port, wpm, listener, killed):
		timeUnit = SECONDS_PER_MINUTE / (COUNTS_PER_WORD * wpm)
		self.createAudioFiles(timeUnit)

		self.curMessage = 0
		self.nextMessage = 0

		self.symbolToAudioFileMap = {
				Symbol.DIT: DIT_FILE,
				Symbol.DAH: DAH_FILE,
				Symbol.CHAR_SPACE: CHAR_SPACE_FILE,
				Symbol.WORD_SPACE: WORD_SPACE_FILE
		}

		self.listener = listener
		self.listener.setServer(server=self)
#		GPIO.setmode(GPIO.BCM)
#		GPIO.setup(LED_CHANNEL, GPIO.OUT, initial=False)
#		GPIO.setup(PLAY_BUTTON_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#		GPIO.setup(DELETE_BUTTON_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_UP)

		# Can probably lower the bouncetime when I get a decent button.
#		GPIO.add_event_detect(PLAY_BUTTON_CHANNEL, GPIO.FALLING, callback=self.playMessage, bouncetime=1000)
#		GPIO.add_event_detect(DELETE_BUTTON_CHANNEL, GPIO.FALLING, callback=self.deleteMessage, bouncetime=1000)

		socket.setdefaulttimeout(1)
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.bind(('', int(port)))
		except socket.error as e:
			fatal("Failed to create socket.  {}: {}".format(e.errno, e.strerror))

		self.sock.listen(10)

		while not killed.is_set():
			try:
				conn, addr = self.sock.accept()
				data = conn.recv(1024)
				conn.close()
				debug("Received message from " + str(addr))
				self.handleMessage(data)
			except socket.timeout:
				continue

	def createAudioFiles(self, timeUnit):
		Popen(['sox', '-n', DIT_FILE, 'synth', str(timeUnit), 'sin', '900'])
		Popen(['sox', '-n', DAH_FILE, 'synth', str(3*timeUnit), 'sin', '900'])
		Popen(['sox', '-n', SYMBOL_SPACE_FILE, 'trim', '0', str(timeUnit)])
		Popen(['sox', '-n', CHAR_SPACE_FILE, 'trim', '0', str(3*timeUnit)])
		Popen(['sox', '-n', WORD_SPACE_FILE, 'trim', '0', str(7*timeUnit)])

		# First second or so seems to get cut off on the Pi, so add 2 seconds of silence to the start
		Popen(['sox', '-n', INIT_SPACE_FILE, 'trim', '0', '2'])

	def handleMessage(self, msg):
		self.createMessageFile(msg)

		self.nextMessage += 1
#		GPIO.output(LED_CHANNEL, GPIO.HIGH)
		debug("LED on.")

	def createMessageFile(self, msg):
		prevIsChar = False
		msgFileList = []
		for byte in msg:
			symbols = self.parseSymbols(byte)

			while symbols:
				symbol = symbols.pop()
				isChar = symbol.isChar()
				if isChar and prevIsChar:
					msgFileList.append(SYMBOL_SPACE_FILE)

				msgFileList.append(self.symbolToAudioFileMap.get(symbol))
				prevIsChar = isChar

		filename = "{}.sox".format(self.nextMessage)
		command = ['sox', INIT_SPACE_FILE]
		command.extend(msgFileList)
		command.append(filename)
		Popen(command)
		Popen(['play', '-q', filename])

	def parseSymbols(self, byte):
		symbols = []
		for i in range(4):
			symbol = Symbol((byte >> i*2) & 0x3)
			symbols.append(symbol)
		return symbols

	def playMessage(self, channel=None):
		debug("Play message.")
		if self.curMessage < self.nextMessage:
			Popen(['play', '-q', "{}.sox".format(self.curMessage)])

	def deleteMessage(self, channel=None):
		debug("delete message.")
		if self.curMessage < self.nextMessage:
			remove("{}.sox".format(self.curMessage))
			self.curMessage += 1

			if self.curMessage == self.nextMessage:
#				GPIO.output(LED_CHANNEL, GPIO.LOW)
				debug("LED off.")


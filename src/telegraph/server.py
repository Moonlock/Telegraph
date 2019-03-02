from src.symbols import Symbol

from collections import deque
from RPi import GPIO
from subprocess import call
import socket
import sys

DEBUG = False

LED_CHANNEL = 16
BUTTON1_CHANNEL = 20
BUTTON2_CHANNEL = 21
COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60

class Server:

	def __init__(self, port, wpm, killed):
		self.messages = deque()
		
		timeUnit = SECONDS_PER_MINUTE / (COUNTS_PER_WORD * wpm)
		self.symbolTimings = self.createTimings(timeUnit)
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(LED_CHANNEL, GPIO.OUT)
		GPIO.setup(BUTTON1_CHANNEL, GPIO.IN)
		GPIO.setup(BUTTON2_CHANNEL, GPIO.IN)
		GPIO.add_event_detect(BUTTON1_CHANNEL, GPIO.RISING, callback=self.playMessage, bouncetime=50)
		GPIO.add_event_detect(BUTTON2_CHANNEL, GPIO.RISING, callback=self.deleteMessage, bouncetime=50)
		
		socket.setdefaulttimeout(1)
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.bind(('', int(port)))
		except socket.error as e:
			print("Failed to create socket.  {}: {}".format(e.errno, e.strerror))
			sys.exit()

		self.sock.listen(10)

		while not killed.is_set():
			try:
				conn, addr = self.sock.accept()
				data = conn.recv(1024)
				conn.close()
				self.handleMessage(data)
			except socket.timeout:
				continue
			
		GPIO.cleanup()
			
	def debug(self, message):
		if DEBUG:
			print(message)

	def createTimings(self, timeUnit):
		return {
			Symbol.DIT: {"duration": timeUnit, "sleep": 2*timeUnit},
			Symbol.DAH: {"duration": 3*timeUnit, "sleep": 4*timeUnit},
			Symbol.CHAR_SPACE: {"duration": 0, "sleep": 3*timeUnit},
			Symbol.WORD_SPACE: {"duration": 0, "sleep": 7*timeUnit},
		}

	def handleMessage(self, msg):
		sonicPiCode = ""
		for byte in msg:
			symbols = self.parseSymbols(byte)
			while symbols:
				symbol = symbols.pop()
				sonicPiCode += self.addSymbolToCode(self.symbolTimings[symbol])

		self.messages.append(sonicPiCode)
		GPIO.output(LED_CHANNEL, GPIO.HIGH)
		self.debug("LED on.")
		call(["sonic_pi", sonicPiCode])

	def parseSymbols(self, byte):
		symbols = []
		for i in range(4):
			symbols.append((byte >> i*2) & 0x3)
		return symbols

	def addSymbolToCode(self, timing):
		code = ""
		if timing["duration"]:
			code = "play 80, release: " + str(timing["duration"]) + ";"
		code += "sleep " + str(timing["sleep"]) + ";"
		return code
	
	def playMessage(self):
		self.debug("Play message.")
		call(["sonic_pi", self.messages[0]])

	def deleteMessage(self):
		self.debug("delete message.")
		if self.messages:
			self.messages.pop()

			if not self.messages:
				GPIO.output(LED_CHANNEL, GPIO.LOW)
				self.debug("LED off.")


from src.symbols import Symbol

from collections import deque
from RPi import GPIO
from subprocess import call
from time import sleep
import socket
import sys

DEBUG = True

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
		GPIO.setup(LED_CHANNEL, GPIO.OUT, initial=False)
		GPIO.setup(BUTTON1_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup(BUTTON2_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		
		# Can probably lower the bouncetime when I get a decent button.
		GPIO.add_event_detect(BUTTON1_CHANNEL, GPIO.RISING, callback=self.playMessage, bouncetime=1000)
		GPIO.add_event_detect(BUTTON2_CHANNEL, GPIO.RISING, callback=self.deleteMessage, bouncetime=1000)
		
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
	
	def playMessage(self, channel):
		self.debug("Play message.")
		#~ sleep(0.040)
		if self.messages:
			call(["sonic_pi", self.messages[0]])

	def deleteMessage(self, channel):
		self.debug("delete message.")
		#~ sleep(0.040)
		if self.messages:
			self.messages.popleft()

			if not self.messages:
				GPIO.output(LED_CHANNEL, GPIO.LOW)
				self.debug("LED off.")


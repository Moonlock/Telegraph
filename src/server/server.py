from symbols import Symbol
from subprocess import call
from threading import Timer
import select
import signal
import socket
import sys


COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60

class Server:

	def __init__(self, port, wpm, killed):
		timeUnit = SECONDS_PER_MINUTE / (COUNTS_PER_WORD * wpm)
		self.symbolTimings = self.createTimings(timeUnit)
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

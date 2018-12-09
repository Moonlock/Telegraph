from symbols import Symbol
from subprocess import call
import signal
import socket
import sys


TIME_UNIT = 0.1

SYMBOL_TIMINGS = {
	Symbol.DIT: {"duration": TIME_UNIT, "sleep": 2*TIME_UNIT},
	Symbol.DAH: {"duration": 3*TIME_UNIT, "sleep": 4*TIME_UNIT},
	Symbol.CHAR_SPACE: {"duration": 0, "sleep": 3*TIME_UNIT},
	Symbol.WORD_SPACE: {"duration": 0, "sleep": 7*TIME_UNIT},
}

class Server:

	def __init__(self, port):
		signal.signal(signal.SIGINT, self.handleSigInt)

		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.bind(('', int(port)))
		except socket.error as e:
			print("Failed to create socket.  {}: {}".format(e.errno, e.strerror))
			sys.exit()

		self.sock.listen(10)

		while True:
			conn, addr = self.sock.accept()
			data = conn.recv(1024)
			conn.close()
			self.handleMessage(data)

	def handleSigInt(self, sig, frame):
		print("Shutting down server.")
		self.sock.close()
		sys.exit()

	def handleMessage(self, msg):
		sonicPiCode = ""
		for byte in msg:
			symbols = self.parseSymbols(byte)
			while symbols:
				symbol = symbols.pop()
				sonicPiCode = self.addSymbolToCode(SYMBOL_TIMINGS[symbol])
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

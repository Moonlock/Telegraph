import socket

from telegraph.common.commonFunctions import debug, fatal
from telegraph.common.symbols import Symbol


COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60


class Server:

	def __init__(self, port, wpm, listener, killed, sendInProgress):
		self.timeUnit = SECONDS_PER_MINUTE / (COUNTS_PER_WORD * wpm)

		self.unplayedMessages = []
		self.sendInProgress = sendInProgress

		self.listener = listener

		self.killed = killed
		self.port = port

	def start(self):
		socket.setdefaulttimeout(1)
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.bind(('', int(self.port)))
		except socket.error as e:
			fatal("Failed to create socket.  {}: {}".format(e.errno, e.strerror))

		self.sock.listen(10)

		while not self.killed.is_set():
			try:
				self.checkUnplayedMessages()
				conn, addr = self.sock.accept()
				data = conn.recv(1024)
				conn.close()
				debug("Received message from " + str(addr))
				self.handleMessage(data)
			except socket.timeout:
				continue

		self.cleanUp()

	def cleanUp(self):
		pass

	def checkUnplayedMessages(self):
		if self.unplayedMessages and not self.sendInProgress.isSet():
			played = self.playMessage(message=self.unplayedMessages[0])
			if played:
				self.unplayedMessages.pop(0)

	def parseMessage(self, msg):
		parsedMsg = []
		for byte in msg:
			parsedMsg.extend(self.parseSymbols(byte))

		return parsedMsg

	def parseSymbols(self, byte):
		symbols = []
		for i in reversed(range(4)):
			symbol = Symbol((byte >> i*2) & 0x3)
			symbols.append(symbol)
		return symbols



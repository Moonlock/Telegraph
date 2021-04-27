from threading import Lock, Thread
from time import sleep
import socket

from telegraph.common.commonFunctions import debug, fatal
from telegraph.common.symbols import Symbol


COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60


class Server:

	def __init__(self, port, wpm, listener, killed, sendInProgress):
		self.timeUnitSec = SECONDS_PER_MINUTE / (COUNTS_PER_WORD * wpm)

		self.messages = []
		self.messagePlayLock = Lock()
		self.unplayedMessages = []
		self.sendInProgress = sendInProgress

		self.play = {Symbol.DIT: self.playDit,
					Symbol.DAH: self.playDah,
					Symbol.CHAR_SPACE: self.playCharSpace,
					Symbol.WORD_SPACE: self.playWordSpace}

		self.listener = listener
		self.listener.setServer(server=self)

		self.killed = killed
		self.port = port

		self.start()

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

	def handleMessage(self, msg):
		parsedMsg = self.parseMessage(msg)
		self.messages.append(parsedMsg)

		self.listener.updateMessageIndicator(len(self.messages))

		if self.sendInProgress.isSet():
			debug("Send in progress, delaying message.")
			self.unplayedMessages.append(parsedMsg)
		elif not self.playMessage(message=parsedMsg):
			self.unplayedMessages.append(parsedMsg)

	def playMessage(self, channel=None, level=None, tick=None, message=None):

		def innerPlayMessage(message):
			prevIsChar = False

			for symbol in message:
				isChar = symbol.isChar()
				if isChar and prevIsChar:
					self.playSymbolSpace()

				self.play[symbol]()
				prevIsChar = isChar

			self.messagePlayLock.release()

		if message is None:
			if not self.messages:
				debug("No message to play.")
				return False
			message = self.messages[0]

		if not self.messagePlayLock.acquire(False):
			debug("Already playing a message.")
			return False

		playThread = Thread(target=innerPlayMessage, args=([message]))
		playThread.start()

		return True

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

	def playDit(self):
		self.listener.playTone(self.timeUnitSec)

	def playDah(self):
		self.listener.playTone(self.timeUnitSec*3)

	def playSymbolSpace(self):
		sleep(self.timeUnitSec)

	def playCharSpace(self):
		sleep(self.timeUnitSec*3)

	def playWordSpace(self):
		sleep(self.timeUnitSec*7)

	def deleteMessage(self, channel=None, level=None, tick=None):
		if self.messages:
			self.messages.pop(0)
			self.listener.updateMessageIndicator(len(self.messages))
		debug("Delete message; {} remaining.".format(len(self.messages)))


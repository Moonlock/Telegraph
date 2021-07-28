from subprocess import Popen, PIPE
from threading import Lock, Thread
from time import sleep
import socket

from telegraph.common.debuggable import Debuggable
from telegraph.common.symbols import Symbol


COUNTS_PER_WORD = 50
SECONDS_PER_MINUTE = 60


class Server(Debuggable):

	def __init__(self, port, wpm, printMessages, listener, destConfig, killed, sendInProgress):
		Debuggable.__init__(self, listener.logMessage)

		self.timeUnitSec = SECONDS_PER_MINUTE / (COUNTS_PER_WORD * wpm)

		self.messages = []
		self.messagePlayLock = Lock()
		self.unplayedMessages = []
		self.sendInProgress = sendInProgress

		self.destConfig = destConfig

		self.play = {Symbol.DIT: self.playDit,
					Symbol.DAH: self.playDah,
					Symbol.CHAR_SPACE: self.playCharSpace,
					Symbol.WORD_SPACE: self.playWordSpace}

		self.listener = listener
		self.listener.setServer(server=self)

		self.killed = killed
		self.port = port
		self.printMessages = printMessages

		self.start()

	def start(self):
		socket.setdefaulttimeout(1)
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.bind(('', int(self.port)))
		except socket.error as e:
			self.fatal("Failed to create socket.  {}: {}".format(e.errno, e.strerror))

		self.sock.listen(10)

		while not self.killed.is_set():
			try:
				self.checkUnplayedMessages()
				conn, addr = self.sock.accept()
				data = conn.recv(1024)
				conn.close()
				self.notice("Received message from {}.".format(self.destConfig.lookupAddress(addr[0])))
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
			self.debug("Send in progress, delaying message.")
			self.unplayedMessages.append(parsedMsg)
		elif not self.playMessage(message=parsedMsg):
			self.unplayedMessages.append(parsedMsg)

		if self.printMessages:
			self.printMessage(parsedMsg)

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
				self.debug("No message to play.")
				return False
			message = self.messages[0]

		if not self.messagePlayLock.acquire(False):
			self.debug("Already playing a message.")
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

	def printMessage(self, message):
		msgString = ""
		for symbol in message:
			msgString += symbol.toString()
		p = Popen(['lp', '-'], stdin=PIPE)
		p.communicate(msgString.encode('utf-8'))

	def deleteMessage(self, channel=None, level=None, tick=None):
		if self.messages:
			self.messages.pop(0)
			self.listener.updateMessageIndicator(len(self.messages))
		self.notice("Delete message; {} remaining.".format(len(self.messages)))


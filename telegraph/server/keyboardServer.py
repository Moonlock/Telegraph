from os import remove
from subprocess import Popen

from telegraph.common.commonFunctions import debug
from telegraph.common.constants import SOUND_FILES_PATH
from telegraph.common.symbols import Symbol
from telegraph.server.server import Server
import telegraph.common.commonFunctions as common


DIT_FILE = SOUND_FILES_PATH + "server-dit.sox"
DAH_FILE = SOUND_FILES_PATH + "server-dah.sox"
SYMBOL_SPACE_FILE = SOUND_FILES_PATH + "server-symbol_space.sox"
CHAR_SPACE_FILE = SOUND_FILES_PATH + "server-char_space.sox"
WORD_SPACE_FILE = SOUND_FILES_PATH + "server-word_space.sox"
INIT_SPACE_FILE = SOUND_FILES_PATH + "server-init_space.sox"

class KeyboardServer(Server):

	def __init__(self, port, wpm, listener, killed, sendInProgress):
		super().__init__(port, wpm, listener, killed, sendInProgress)

		self.createAudioFiles()

		self.curMessage = 0
		self.nextMessage = 0
		self.messageProcess = None

		self.symbolToAudioFileMap = {
				Symbol.DIT: DIT_FILE,
				Symbol.DAH: DAH_FILE,
				Symbol.CHAR_SPACE: CHAR_SPACE_FILE,
				Symbol.WORD_SPACE: WORD_SPACE_FILE
		}

		self.listener.setServer(server=self)
		self.start()

	def cleanUp(self):
		common.deleteFiles(SOUND_FILES_PATH, "message-", ".sox")
		common.deleteFiles(SOUND_FILES_PATH, "server-", ".sox")

	def createAudioFiles(self):
		Popen(['sox', '-n', DIT_FILE, 'synth', str(self.timeUnit), 'sin', '900'])
		Popen(['sox', '-n', DAH_FILE, 'synth', str(3*self.timeUnit), 'sin', '900'])
		Popen(['sox', '-n', SYMBOL_SPACE_FILE, 'trim', '0', str(self.timeUnit)])
		Popen(['sox', '-n', CHAR_SPACE_FILE, 'trim', '0', str(3*self.timeUnit)])
		Popen(['sox', '-n', WORD_SPACE_FILE, 'trim', '0', str(7*self.timeUnit)])

		# First second or so seems to get cut off on the Pi, so add 2 seconds of silence to the start
		Popen(['sox', '-n', INIT_SPACE_FILE, 'trim', '0', '2'])

	def handleMessage(self, msg):
		self.createMessageFile(msg)
		newMessage = self.nextMessage
		self.nextMessage += 1

		self.listener.updateMessageIndicator(self.nextMessage - self.curMessage)

		if self.sendInProgress.isSet():
			debug("Send in progress, delaying message.")
			self.unplayedMessages.append(newMessage)
		elif not self.playMessage(message=newMessage):
			self.unplayedMessages.append(newMessage)

	def createMessageFile(self, msg):
		prevIsChar = False
		msgFileList = []
		msgSymbols = self.parseMessage(msg)
		for symbol in msgSymbols:
			isChar = symbol.isChar()
			if isChar and prevIsChar:
				msgFileList.append(SYMBOL_SPACE_FILE)

			msgFileList.append(self.symbolToAudioFileMap.get(symbol))
			prevIsChar = isChar

		filename = "{}message-{}.sox".format(SOUND_FILES_PATH, self.nextMessage)
		common.concatAudioFiles(msgFileList, filename)

	def playMessage(self, channel=None, message=None):
		if self.messageProcess and self.messageProcess.poll() is None:
			debug("Already playing a message.")
			return False

		messageNum = message if message is not None else self.curMessage

		if messageNum < self.nextMessage:
			debug("Play message {}.".format(messageNum))
			self.messageProcess = Popen(['play', '-q', "{}message-{}.sox".format(SOUND_FILES_PATH, messageNum)])
		else:
			debug("No message to play.")

		return True

	def deleteMessage(self, channel=None):
		debug("delete message.")
		if self.curMessage < self.nextMessage:
			remove("{}message-{}.sox".format(SOUND_FILES_PATH, self.curMessage))
			self.curMessage += 1

			self.listener.updateMessageIndicator(self.nextMessage - self.curMessage)


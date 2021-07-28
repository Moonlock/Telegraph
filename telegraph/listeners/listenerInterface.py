from telegraph.common.clientMode import ClientMode
from telegraph.common.debuggable import Debuggable

class ListenerInterface(Debuggable):

	def __init__(self):
		Debuggable.__init__(self, self.logMessage)

		self.clientConfigured = False
		self.serverConfigured = False
		self.server = None

		self.mode = ClientMode.INIT
		self.callbacks = {ClientMode.INIT: lambda: self.fatal("Callback not defined."),
						ClientMode.MAIN: lambda: self.fatal("Callback not defined.")}

	def setMode(self, mode):
		self.mode = mode

	def setupCallbacks(self):
		pass

	def startMessage(self):
		pass

	def error(self, message):
		pass

	def sendSuccess(self):
		pass

	def playTone(self, duration):
		pass

	def updateMessageIndicator(self, messages):
		pass

	def logMessage(self, message):
		pass

	def setClientCallback(self, initCallback, mainCallback):
		self.callbacks = {ClientMode.INIT: initCallback,
						ClientMode.MAIN: mainCallback}
		self.clientConfigured = True

	def setServer(self, server):
		self.serverConfigured = True
		self.server = server

	def isReady(self):
		return self.serverConfigured and self.clientConfigured

	def start(self):
		pass

	def cleanUp(self):
		pass
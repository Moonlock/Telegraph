from telegraph.common.clientMode import ClientMode
from telegraph.common.commonFunctions import fatal

class ListenerInterface:

	def __init__(self):
		self.clientConfigured = False
		self.serverConfigured = False
		self.server = None

		self.mode = ClientMode.INIT
		self.callbacks = {ClientMode.INIT: lambda: fatal("Callback not defined."),
						ClientMode.MAIN: lambda: fatal("Callback not defined.")}

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

	def updateMessageIndicator(self, messages):
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
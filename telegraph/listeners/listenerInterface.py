from telegraph.common.clientMode import ClientMode
from telegraph.common.commonFunctions import fatal

class ListenerInterface:

	def __init__(self):
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

	def setServer(self, server):
		pass

	def cleanUp(self):
		pass
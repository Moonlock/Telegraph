class ListenerInterface:

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

	def resetClientCallback(self, pressCallback, releaseCallback):
		pass

	def setServer(self, server):
		pass

	def cleanUp(self):
		pass
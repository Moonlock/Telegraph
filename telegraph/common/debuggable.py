import sys
import telegraph.common.commonFunctions as common

class Debuggable():

	def __init__(self, outputFunction):
		self.output = outputFunction

	def debug(self, message):
		if common.isDebugEnabled():
			self.output(message)

	def notice(self, message):
		self.output(message)

	def fatal(self, message):
		# pygame will close, so print output to terminal.
		common.fatal(message)

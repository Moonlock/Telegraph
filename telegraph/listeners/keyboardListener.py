from time import time
import os
import signal
import sys

from pynput import keyboard

from telegraph.common.commonFunctions import debug
from telegraph.common.commonFunctions import fatal
import termios


USEC_PER_SECOND = 1000000


class KeyboardListener(ListenerInterface):

	def __init__(self):
		self.pressCallback = lambda: fatal("Press callback not defined.")
		self.releaseCallback = lambda: fatal("Release callback not defined.")
		self.server = None

		self.lastPress = 0
		self.lastRelease = 0

		self.ctrlPressed = False
		self.telegraphKeyPressed = False

		self.serverConfigured = False
		self.clientConfigured = False
		self.hasStarted = False

		self.oldSettings = termios.tcgetattr(sys.stdin.fileno())

	def setupCallbacks(self):
		def innerPressCallback(key):
			if key == keyboard.Key.space and not self.telegraphKeyPressed:
				self.telegraphKeyPressed = True
				self.pressCallback(self.timeRelease())

			if key == keyboard.Key.enter:
				self.server.playMessage()
			if key == keyboard.Key.delete or key == keyboard.Key.backspace:
				self.server.deleteMessage()

			if key == keyboard.Key.ctrl:
				self.ctrlPressed = True
			if self.ctrlPressed and key == keyboard.KeyCode(char='c'):
				os.kill(os.getpid(), signal.SIGINT)
				return False

		def innerReleaseCallback(key):
			if key == keyboard.Key.space:
				self.telegraphKeyPressed = False
				self.releaseCallback(self.timePress())

			if key == keyboard.Key.ctrl:
				self.ctrlPressed = False

		newSettings = termios.tcgetattr(sys.stdin.fileno())
		newSettings[3] = newSettings[3] & ~termios.ECHO

		termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, newSettings)
		listener = keyboard.Listener(on_press=innerPressCallback, on_release=innerReleaseCallback)
		listener.start()

	def timePress(self):
		self.lastRelease = time()
		pressTime = (self.lastRelease - self.lastPress) * USEC_PER_SECOND
		debug("Press: " + str(int(pressTime/1000)))
		return pressTime

	def timeRelease(self):
		self.lastPress = time()
		releaseTime = (self.lastPress - self.lastRelease) * USEC_PER_SECOND
		debug("Release: " + str(int(releaseTime/1000)))
		return releaseTime

	def startMessage(self):
		print("Start message")

	def error(self, message):
		print(message)

	def sendSuccess(self):
		print("Message sent")

	def updateMessageIndicator(self, messages):
		print("Messages: " + str(messages) + ".")

	def resetClientCallback(self, pressCallback, releaseCallback):
		self.pressCallback = pressCallback
		self.releaseCallback = releaseCallback

		self.clientConfigured = True
		self.checkReady()

	def setServer(self, server):
		self.server = server

		self.serverConfigured = True
		self.checkReady()

	def checkReady(self):
		if not self.hasStarted and self.serverConfigured and self.clientConfigured:
			self.hasStarted = True
			self.setupCallbacks()

	def cleanUp(self):
		termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.oldSettings)



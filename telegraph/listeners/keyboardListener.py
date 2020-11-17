import os
import signal
import sys

from pynput import keyboard
import telegraph.common.commonFunctions as common

import termios


class KeyboardListener:

	def __init__(self):
		self.pressCallback = lambda: common.fatal("Press callback not defined.")
		self.releaseCallback = lambda: common.fatal("Release callback not defined.")
		self.server = None

		self.ctrlPressed = False
		self.telegraphKeyPressed = False

		self.oldSettings = termios.tcgetattr(sys.stdin.fileno())
		self.setupCallbacks()

	def setupCallbacks(self):
		def innerPressCallback(key):
			if key == keyboard.Key.space and not self.telegraphKeyPressed:
				self.telegraphKeyPressed = True
				self.pressCallback()

			if key == keyboard.Key.ctrl:
				self.ctrlPressed = True
			if self.ctrlPressed and key == keyboard.KeyCode(char='c'):
				os.kill(os.getpid(), signal.SIGINT)
				return False

		def innerReleaseCallback(key):
			if key == keyboard.Key.space:
				self.telegraphKeyPressed = False
				self.releaseCallback()

			if key == keyboard.Key.enter:
				self.server.playMessage()
			if key == keyboard.Key.delete or key == keyboard.Key.backspace:
				self.server.deleteMessage()

			if key == keyboard.Key.ctrl:
				self.ctrlPressed = False

		newSettings = termios.tcgetattr(sys.stdin.fileno())
		newSettings[3] = newSettings[3] & ~termios.ECHO

		termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, newSettings)
		listener = keyboard.Listener(on_press=innerPressCallback, on_release=innerReleaseCallback)
		listener.start()

	def startMessage(self):
		print("Start")

	def error(self):
		pass

	def sendSuccess(self):
		pass

	def updateMessageIndicator(self, messages):
		print("Messages: " + str(messages) + ".")

	def resetClientCallback(self, pressCallback, releaseCallback):
		self.pressCallback = pressCallback
		self.releaseCallback = releaseCallback

	def setServer(self, server):
		self.server = server

	def cleanUp(self):
		termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.oldSettings)



import os
import signal
import sys

from pynput import keyboard
import src.commonFunctions as common

import termios


class KeyboardListener:

	def __init__(self):
		self.pressCallback = lambda: common.fatal("Press callback not defined.")
		self.releaseCallback = lambda: common.fatal("Release callback not defined.")
		self.ctrlPressed = False
		self.pressed = False

		self.oldSettings = termios.tcgetattr(sys.stdin.fileno())
		self.setupCallbacks()

	def setupCallbacks(self):
		def innerPressCallback(key):
			if key == keyboard.Key.space and not self.pressed:
				self.pressed = True
				self.pressCallback()

			if key == keyboard.Key.ctrl:
				self.ctrlPressed = True
			if self.ctrlPressed and key == keyboard.KeyCode(char='c'):
				os.kill(os.getpid(), signal.SIGINT)
				return False

		def innerReleaseCallback(key):
			if key == keyboard.Key.space:
				self.pressed = False
				self.releaseCallback()

			if key == keyboard.Key.enter:
				self.server.playMessage()
			if key == keyboard.Key.delete:
				self.server.deleteMessage()

			if key == keyboard.Key.ctrl:
				self.ctrlPressed = False

		newSettings = termios.tcgetattr(sys.stdin.fileno())
		newSettings[3] = newSettings[3] & ~termios.ECHO

		termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, newSettings)
		listener = keyboard.Listener(on_press=innerPressCallback, on_release=innerReleaseCallback)
		listener.start()

	def resetClientCallback(self, gpioCallback=None, pressCallback=None, releaseCallback=None):
		self.pressCallback = pressCallback
		self.releaseCallback = releaseCallback

	def setServer(self, server):
		self.server = server

	def cleanUp(self):
		termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.oldSettings)



from time import time, sleep
import os
import pygame
import signal

from telegraph.common.commonFunctions import debug
from telegraph.listeners.listenerInterface import ListenerInterface


USEC_PER_SECOND = 1000000


class KeyboardListener(ListenerInterface):

	def __init__(self, handleSigInt):
		super().__init__()

		self.lastPress = 0
		self.lastRelease = 0

		signal.signal(signal.SIGINT, handleSigInt)

	def start(self):
		pygame.init()
		pygame.display.set_mode((800, 600))

		running = True
		while running:
			for event in pygame.event.get():

				if event.type == pygame.QUIT:
					os.kill(os.getpid(), signal.SIGINT)
					running = False

				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
						os.kill(os.getpid(), signal.SIGINT)
						running = False

					elif event.key == pygame.K_SPACE:
						self.callbacks[self.mode](True, self.timeRelease())

					elif event.key == pygame.K_RETURN:
						self.server.playMessage()

					elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
						self.server.deleteMessage()

				elif event.type == pygame.KEYUP:
					if event.key == pygame.K_SPACE:
						self.callbacks[self.mode](False, self.timePress())

			sleep(0.010)

	def timePress(self):
		self.lastRelease = time()
		pressTimeUsec = (self.lastRelease - self.lastPress) * USEC_PER_SECOND
		debug("Press: " + str(int(pressTimeUsec/1000)))
		return pressTimeUsec

	def timeRelease(self):
		self.lastPress = time()
		releaseTimeUsec = (self.lastPress - self.lastRelease) * USEC_PER_SECOND
		debug("Release: " + str(int(releaseTimeUsec/1000)))
		return releaseTimeUsec

	def startMessage(self):
		print("Start message")

	def error(self, message):
		print(message)

	def sendSuccess(self):
		print("Message sent")

	def updateMessageIndicator(self, messages):
		print("Messages: " + str(messages) + ".")


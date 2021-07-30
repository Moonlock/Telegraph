from time import time, sleep
import os
import signal

import numpy
import pygame
import pygame.freetype

from telegraph.listeners.listenerInterface import ListenerInterface


NUM_LOG_MESSAGES = 24

FREQUENCY = 800
SAMPLE_RATE = 44100

USEC_PER_SECOND = 1000000


class KeyboardListener(ListenerInterface):

	def __init__(self, buzzOnSend, handleSigInt):
		ListenerInterface.__init__(self)

		self.lastPress = 0
		self.lastRelease = 0
		self.buzzOnSend = buzzOnSend

		signal.signal(signal.SIGINT, handleSigInt)

	def start(self):
		pygame.init()

		self.screen = pygame.display.set_mode((800, 600))
		self.font = pygame.freetype.SysFont("Monospace", 20)
		self.fontColour = (255, 255, 255)
		self.logPos = [(0, 25*i) for i in range(NUM_LOG_MESSAGES)]
		self.logMessages = []

		samples = numpy.arange(SAMPLE_RATE)
		buffer = numpy.sin(2*numpy.pi * samples * FREQUENCY / SAMPLE_RATE).astype(numpy.float32)
		self.buzzer = pygame.mixer.Sound(buffer)

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
		if(self.buzzOnSend):
			self.buzzer.stop()

		self.lastRelease = time()
		pressTimeUsec = (self.lastRelease - self.lastPress) * USEC_PER_SECOND
		self.debug("Press: " + str(int(pressTimeUsec/1000)))

		return pressTimeUsec

	def timeRelease(self):
		if(self.buzzOnSend):
			self.buzzer.play(-1)

		self.lastPress = time()
		releaseTimeUsec = (self.lastPress - self.lastRelease) * USEC_PER_SECOND
		self.debug("Release: " + str(int(releaseTimeUsec/1000)))

		return releaseTimeUsec

	def startMessage(self):
		self.notice("Start message")

	def error(self, message):
		self.notice(message)

	def fatal(self, message):
		pygame.quit()
		os.kill(os.getpid(), signal.SIGINT)
		super().fatal(message)

	def sendSuccess(self):
		self.notice("Message sent")

	def playTone(self, duration):
		samples = numpy.arange(SAMPLE_RATE * duration)
		buffer = numpy.sin(2*numpy.pi * samples * FREQUENCY / SAMPLE_RATE).astype(numpy.float32)
		sound = pygame.mixer.Sound(buffer)
		sound.play()

		pygame.time.delay(int(duration * 1000))

	def updateMessageIndicator(self, messages):
		self.notice("Messages: " + str(messages) + ".")

	def logMessage(self, message):
		self.logMessages.append(message)
		if len(self.logMessages) > NUM_LOG_MESSAGES:
			self.logMessages.pop(0)

		self.screen.fill((0,0,0))
		for i, msg in enumerate(self.logMessages):
			self.font.render_to(self.screen, self.logPos[i], msg, self.fontColour)

		pygame.display.flip()


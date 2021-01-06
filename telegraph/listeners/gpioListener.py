from threading import Timer

from telegraph.common.commonFunctions import debug, fatal
import pigpio


KEY_CHANNEL = 4
LED_CHANNEL = 16
PLAY_BUTTON_CHANNEL = 20
DELETE_BUTTON_CHANNEL = 21
RED=13
GREEN=19


class GpioListener:

	def __init__(self):
		self.pressCallback = lambda: fatal("Press callback not defined.")
		self.releaseCallback = lambda: fatal("Release callback not defined.")

		self.pi = pigpio.pi()

		self.setupCallbacks()

	def setupCallbacks(self):

		def innerCallback(channel, level, tick):
			if level == 0:
				self.pressCallback()
			else:
				self.releaseCallback()

		self.pi.set_mode(KEY_CHANNEL, pigpio.INPUT)
		self.pi.callback(KEY_CHANNEL, pigpio.EITHER_EDGE, innerCallback)
		self.pi.set_glitch_filter(KEY_CHANNEL, 10000)

		self.pi.set_mode(LED_CHANNEL, pigpio.OUTPUT)
		self.pi.set_mode(RED, pigpio.OUTPUT)
		self.pi.set_mode(GREEN, pigpio.OUTPUT)
		self.pi.write(LED_CHANNEL, 0)
		self.pi.write(RED, 0)
		self.pi.write(GREEN, 0)

		self.pi.set_mode(PLAY_BUTTON_CHANNEL, pigpio.INPUT)
		self.pi.set_mode(DELETE_BUTTON_CHANNEL, pigpio.INPUT)
		self.pi.set_pull_up_down(PLAY_BUTTON_CHANNEL, pigpio.PUD_UP)
		self.pi.set_pull_up_down(DELETE_BUTTON_CHANNEL, pigpio.PUD_UP)

	def updateMessageIndicator(self, messages):
		if messages:
			self.pi.write(LED_CHANNEL, 1)
		else:
			self.pi.write(LED_CHANNEL, 0)

	def resetClientCallback(self, pressCallback, releaseCallback):
		self.pressCallback = pressCallback
		self.releaseCallback = releaseCallback

	def startMessage(self):
		self.turnOffRgbLed()
		self.pi.write(RED, 1)
		self.pi.hardware_PWM(GREEN, 100, 250000)

	def error(self, message):
		debug(message)
		self.turnOffRgbLed()
		self.pi.write(RED, 1)
		Timer(2, self.turnOffRgbLed).start()

	def sendSuccess(self):
		self.turnOffRgbLed()
		self.pi.write(GREEN, 1)
		Timer(2, self.turnOffRgbLed).start()

	def turnOffRgbLed(self):
		self.pi.hardware_PWM(GREEN, 100, 0)
		self.pi.write(RED, 0)
		self.pi.write(GREEN, 0)

	def setServer(self, server):
		# Can probably lower the bouncetime when I get a decent button.
		self.pi.callback(PLAY_BUTTON_CHANNEL, pigpio.FALLING_EDGE, server.playMessage)
		self.pi.callback(DELETE_BUTTON_CHANNEL, pigpio.FALLING_EDGE, server.deleteMessage)
		self.pi.set_glitch_filter(PLAY_BUTTON_CHANNEL, 100000)
		self.pi.set_glitch_filter(DELETE_BUTTON_CHANNEL, 100000)

	def cleanUp(self):
		self.pi.stop()



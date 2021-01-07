from threading import Timer

from telegraph.common.commonFunctions import debug, fatal
import pigpio


KEY_CHANNEL = 4
MESSAGE_LED_CHANNEL = 16
PLAY_BUTTON_CHANNEL = 20
DELETE_BUTTON_CHANNEL = 21
RED_LED_CHANNEL=13
GREEN_LED_CHANNEL=19

# Config for green LED PWM when making yellow light
DUTY_CYCLE = 250000
FREQUENCY = 100

USEC_PER_MSEC = 1000
TICK_ROLLOVER = 4294967296


class GpioListener:

	def __init__(self):
		self.pressCallback = lambda: fatal("Press callback not defined.")
		self.releaseCallback = lambda: fatal("Release callback not defined.")

		self.pi = pigpio.pi()

		self.lastTick = 0
		self.setupCallbacks()

	def keyCallback(self, channel, level, tick):
		elapsedTime = tick - self.lastTick
		if elapsedTime < 0:
			elapsedTime += TICK_ROLLOVER

		if level == 0:
			debug("Release: " + str(int(elapsedTime/1000)))
			self.pressCallback(elapsedTime)
		else:
			debug("Press: " + str(int(elapsedTime/1000)))
			self.releaseCallback(elapsedTime)

		self.lastTick = tick

	def setupCallbacks(self):
		self.pi.set_mode(KEY_CHANNEL, pigpio.INPUT)
		self.pi.callback(KEY_CHANNEL, pigpio.EITHER_EDGE, self.keyCallback)
		self.pi.set_glitch_filter(KEY_CHANNEL, 10 * USEC_PER_MSEC)

		self.pi.set_mode(MESSAGE_LED_CHANNEL, pigpio.OUTPUT)
		self.pi.set_mode(RED_LED_CHANNEL, pigpio.OUTPUT)
		self.pi.set_mode(GREEN_LED_CHANNEL, pigpio.OUTPUT)
		self.pi.write(MESSAGE_LED_CHANNEL, 0)
		self.pi.write(RED_LED_CHANNEL, 0)
		self.pi.write(GREEN_LED_CHANNEL, 0)

		self.pi.set_mode(PLAY_BUTTON_CHANNEL, pigpio.INPUT)
		self.pi.set_mode(DELETE_BUTTON_CHANNEL, pigpio.INPUT)
		self.pi.set_pull_up_down(PLAY_BUTTON_CHANNEL, pigpio.PUD_UP)
		self.pi.set_pull_up_down(DELETE_BUTTON_CHANNEL, pigpio.PUD_UP)

	def updateMessageIndicator(self, messages):
		if messages:
			self.pi.write(MESSAGE_LED_CHANNEL, 1)
		else:
			self.pi.write(MESSAGE_LED_CHANNEL, 0)

	def resetClientCallback(self, pressCallback, releaseCallback):
		self.pressCallback = pressCallback
		self.releaseCallback = releaseCallback

	def startMessage(self):
		self.turnOffRgbLed()
		self.pi.write(RED_LED_CHANNEL, 1)
		self.pi.hardware_PWM(GREEN_LED_CHANNEL, FREQUENCY, DUTY_CYCLE)

	def error(self, message):
		debug(message)
		self.turnOffRgbLed()
		self.pi.write(RED_LED_CHANNEL, 1)
		Timer(2, self.turnOffRgbLed).start()

	def sendSuccess(self):
		self.turnOffRgbLed()
		self.pi.write(GREEN_LED_CHANNEL, 1)
		Timer(2, self.turnOffRgbLed).start()

	def turnOffRgbLed(self):
		self.pi.hardware_PWM(GREEN_LED_CHANNEL, FREQUENCY, 0)
		self.pi.write(RED_LED_CHANNEL, 0)
		self.pi.write(GREEN_LED_CHANNEL, 0)

	def setServer(self, server):
		self.pi.callback(PLAY_BUTTON_CHANNEL, pigpio.FALLING_EDGE, server.playMessage)
		self.pi.callback(DELETE_BUTTON_CHANNEL, pigpio.FALLING_EDGE, server.deleteMessage)
		self.pi.set_glitch_filter(PLAY_BUTTON_CHANNEL, 100 * USEC_PER_MSEC)
		self.pi.set_glitch_filter(DELETE_BUTTON_CHANNEL, 100 * USEC_PER_MSEC)

	def cleanUp(self):
		self.turnOffRgbLed()
		self.pi.stop()



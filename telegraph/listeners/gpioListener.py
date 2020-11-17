from threading import Timer

from RPi import GPIO
import telegraph.common.commonFunctions as common


KEY_CHANNEL = 4
LED_CHANNEL = 16
PLAY_BUTTON_CHANNEL = 20
DELETE_BUTTON_CHANNEL = 21
RED=13
GREEN=19
BLUE=26


class GpioListener:

	def __init__(self):
		self.pressCallback = lambda: common.fatal("Press callback not defined.")
		self.releaseCallback = lambda: common.fatal("Release callback not defined.")

		self.setupCallbacks()

	def setupCallbacks(self):

		def innerCallback(channel):
			if GPIO.input(channel) == 0:
				self.pressCallback()
			else:
				self.releaseCallback()

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(KEY_CHANNEL, GPIO.IN)
		GPIO.add_event_detect(KEY_CHANNEL, GPIO.BOTH, callback=innerCallback, bouncetime=20)

		GPIO.setup(LED_CHANNEL, GPIO.OUT, initial=False)
		GPIO.setup(PLAY_BUTTON_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(DELETE_BUTTON_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	def updateMessageIndicator(self, messages):
		if messages:
			GPIO.output(LED_CHANNEL, GPIO.HIGH)
		else:
			GPIO.output(LED_CHANNEL, GPIO.LOW)

	def resetClientCallback(self, pressCallback, releaseCallback):
		self.pressCallback = pressCallback
		self.releaseCallback = releaseCallback

	def startMessage(self):
		self.turnOffRgbLed()
		GPIO.output(RED, GPIO.HIGH)
		p = GPIO.PWM(GREEN, 100)
		p.start(25)

	def error(self):
		self.turnOffRgbLed()
		GPIO.output(RED, GPIO.HIGH)
		Timer(2, self.turnOffRgbLed).start()

	def sendSuccess(self):
		self.turnOffRgbLed()
		GPIO.output(GREEN, GPIO.HIGH)
		Timer(2, self.turnOffRgbLed).start()

	def turnOffRgbLed(self):
		GPIO.output(RED, GPIO.LOW)
		GPIO.output(GREEN, GPIO.LOW)
		GPIO.output(BLUE, GPIO.LOW)

	def setServer(self, server):
		# Can probably lower the bouncetime when I get a decent button.
		GPIO.add_event_detect(PLAY_BUTTON_CHANNEL, GPIO.FALLING, callback=server.playMessage, bouncetime=1000)
		GPIO.add_event_detect(DELETE_BUTTON_CHANNEL, GPIO.FALLING, callback=server.deleteMessage, bouncetime=1000)

	def cleanUp(self):
		GPIO.cleanup()



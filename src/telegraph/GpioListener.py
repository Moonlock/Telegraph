import sys

from RPi import GPIO
import src.commonFunctions as common
import termios


KEY_CHANNEL = 4
LED_CHANNEL = 16
PLAY_BUTTON_CHANNEL = 20
DELETE_BUTTON_CHANNEL = 21

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

	def setServer(self, server):
		# Can probably lower the bouncetime when I get a decent button.
		GPIO.add_event_detect(PLAY_BUTTON_CHANNEL, GPIO.FALLING, callback=server.playMessage, bouncetime=1000)
		GPIO.add_event_detect(DELETE_BUTTON_CHANNEL, GPIO.FALLING, callback=server.deleteMessage, bouncetime=1000)

	def cleanUp(self):
		termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.oldSettings)



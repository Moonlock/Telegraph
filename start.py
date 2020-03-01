#! /usr/bin/python3

from threading import Thread, Event
import configparser
import signal

from src import constants
from src.commonFunctions import fatal
from src.telegraph import client
from src.telegraph import server
from src.telegraph.keyboardListener import KeyboardListener

try:
	from RPi import GPIO
	from src.telegraph.GpioListener import GpioListener
	usingGpio = True
except ImportError:
	usingGpio = False


config = configparser.ConfigParser()
config.read(constants.CONFIG_FILE)
if not config.sections():
	fatal("Error reading config file.")
if config['Common'].getint('Version') != constants.CONFIG_FILE_VERSION:
	fatal("Config file version mismatch; please recreate.")

killed = Event()

clientConfig = config['Client']
multiDest = clientConfig.getboolean('Multiple Destinations')
if multiDest:
	serverAddress = None
	serverPort = None
else:
	serverAddress = clientConfig['Address']
	serverPort = clientConfig['Port']

listener = GpioListener() if usingGpio else KeyboardListener()

clientThread = Thread(target=client.Client, args=(multiDest, serverAddress, serverPort, listener, killed))
clientThread.start()

serverConfig = config['Server']
listenPort = serverConfig['Port']
wpm = int(serverConfig['WPM'])

serverThread = Thread(target=server.Server, args=(listenPort, wpm, listener, killed))
serverThread.start()

def handleSigInt(sig, frame):
	killed.set()
	clientThread.join()
	serverThread.join()
	if usingGpio:
		GPIO.cleanup()

signal.signal(signal.SIGINT, handleSigInt)

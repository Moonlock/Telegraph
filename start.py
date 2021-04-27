#! /usr/bin/python3

from threading import Thread, Event
from time import sleep
import configparser
import signal

from telegraph.client import client
from telegraph.common import constants
from telegraph.common.commonFunctions import fatal
from telegraph.server import server


try:
	from telegraph.listeners.gpioListener import GpioListener
#	from telegraph.server.piServer import PiServer
	usingGpio = True
except ImportError:
	from telegraph.listeners.keyboardListener import KeyboardListener
#	from telegraph.server.keyboardServer import KeyboardServer
	usingGpio = False


config = configparser.ConfigParser()
config.read(constants.CONFIG_FILE)
if not config.sections():
	fatal("Error reading config file.")
if config['Common'].getint('Version') != constants.CONFIG_FILE_VERSION:
	fatal("Config file version mismatch; please recreate.")


killed = Event()
sendInProgress = Event()

def handleSigInt(sig, frame):
	killed.set()
	clientThread.join()
	serverThread.join()

signal.signal(signal.SIGINT, handleSigInt)

clientConfig = config['Client']
multiDest = clientConfig.getboolean('Multiple Destinations')
if multiDest:
	serverAddress = None
	serverPort = None
else:
	serverAddress = clientConfig['Address']
	serverPort = clientConfig['Port']

listener = GpioListener() if usingGpio else KeyboardListener(handleSigInt)
#server = PiServer if usingGpio else KeyboardServer

clientThread = Thread(target=client.Client, args=(multiDest, serverAddress, serverPort, listener, killed, sendInProgress))
clientThread.start()

serverConfig = config['Server']
listenPort = serverConfig['Port']
wpm = int(serverConfig['WPM'])

serverThread = Thread(target=server.Server, args=(listenPort, wpm, listener, killed, sendInProgress))
serverThread.start()

while not listener.isReady():
	sleep(0.1)
listener.start()


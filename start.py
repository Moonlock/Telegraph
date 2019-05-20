#! /usr/bin/python3

from src.telegraph import client
from src.telegraph import server
import configparser
import setup
import signal
import sys
from RPi import GPIO
from threading import Thread, Event

config = configparser.ConfigParser()
config.read(setup.CONFIG_FILE)
if not config.sections():
	print('Running setup script.')
	setup.main()
	config.read(setup.CONFIG_FILE)
	if not config.sections():
		sys.exit()

killed = Event()

commonConfig = config['Common']
debug = commonConfig.getboolean('Debug')

clientConfig = config['Client']
multiDest = clientConfig.getboolean('Multiple Destinations')
if multiDest:
	serverAddress = None
	serverPort = None
else:
	serverAddress = clientConfig['Address']
	serverPort = clientConfig['Port']

clientThread = Thread(target=client.Client, args=(multiDest, serverAddress, serverPort, killed, debug))
clientThread.start()

serverConfig = config['Server']
listenPort = serverConfig['Port']
wpm = int(serverConfig['WPM'])

serverThread = Thread(target=server.Server, args=(listenPort, wpm, killed, debug))
serverThread.start()

def handleSigInt(sig, frame):
	killed.set()
	clientThread.join()
	serverThread.join()
	GPIO.cleanup()

signal.signal(signal.SIGINT, handleSigInt)

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

clientConfig = config['Client']
serverAddress = clientConfig['Address']
clientPort = clientConfig['Port']

clientThread = Thread(target=client.Client, args=(serverAddress, clientPort, killed))
clientThread.start()

serverConfig = config['Server']
serverPort = serverConfig['Port']
wpm = int(serverConfig['WPM'])

serverThread = Thread(target=server.Server, args=(serverPort, wpm, killed))
serverThread.start()

def handleSigInt(sig, frame):
	killed.set()
	clientThread.join()
	serverThread.join()
	GPIO.cleanup()

signal.signal(signal.SIGINT, handleSigInt)

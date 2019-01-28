#! /usr/bin/python3

from client import client
from server import server
import configparser
import setup
import signal
from threading import Thread, Event

config = configparser.ConfigParser()
config.read('config.ini')
if not config.sections():
	print('Config file not found.')
	response = input('Run setup script? [y/N]: ' or 'n')
	if response.lower() == 'y':
		setup.main()
		config.read('config.ini')
		if not config.sections():
			exit()
	else:
		exit()

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

signal.signal(signal.SIGINT, handleSigInt)

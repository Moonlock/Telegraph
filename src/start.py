#! /usr/bin/python3

from client import client
from server import server
import configparser
import setup

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

clientConfig = config['Client']
server = clientConfig['Address']
clientPort = clientConfig['Port']

client = Thread(target=client.Client, args=(server, clientPort))
client.start()

serverConfig = config['Server']
serverPort = serverConfig['Port']
wpm = int(serverConfig['WPM'])

server = Thread(target=server.Server, args=(serverPort, wpm))
server.start()

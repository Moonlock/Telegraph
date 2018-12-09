#! /usr/bin/python3

from client import client
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
	else:
		exit()

clientConfig = config['Client']
server = clientConfig['Address']
port = clientConfig['Port']

client = client.Client(server, port)

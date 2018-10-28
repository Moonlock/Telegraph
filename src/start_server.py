#! /usr/bin/python3

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
	else:
		exit()

serverConfig = config['Server']
port = serverConfig['Port']

server.run(port)

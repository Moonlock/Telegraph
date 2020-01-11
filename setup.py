#! /usr/bin/python3

import configparser
import os.path
import sys

from src.commonFunctions import writeConfig

CONFIG_FILE = 'resources/config.ini'
CONTACTS_FILE = 'resources/contacts.ini'
GROUPS_FILE = 'resources/groups.ini'

def main():

	try:
		if os.path.isfile(CONFIG_FILE):
			response = input('Config file already exists.  Recreate? [y/N]: ' or 'n')
			if response.lower() != 'y':
				sys.exit()

		serverConfig = {}
		clientConfig = {}
		commonConfig = {}
		serverConfig['WPM'] = input('WPM playback speed [20]: ') or 20
		serverConfig['Port'] = input('Local port [8000]: ') or 8000

		multiDest = input('Enable multiple destinations [y/N]: ') or 'n'
		multiDest = multiDest.lower() == 'y'
		clientConfig['Multiple Destinations'] = multiDest
		if not multiDest:
			clientConfig['Address'] = input('Remote IP address/hostname [localhost]: ') or 'localhost'
			clientConfig['Port'] = input('Remote port [8000]: ') or 8000
		debug = input('Enable debug info [y/N]: ') or 'n'
		commonConfig['Debug'] = debug.lower() == 'y'

	except KeyboardInterrupt:
		sys.exit()

	config = configparser.ConfigParser()
	config['Server'] = serverConfig
	config['Client'] = clientConfig
	config['Common'] = commonConfig
	writeConfig(CONFIG_FILE, config)

	if multiDest:
		print("")
		print("Use `./configureContacts` to create contacts and groups.")

if __name__ == '__main__':
	main()

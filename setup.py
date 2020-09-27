#! /usr/bin/python3

import configparser
import os.path
import sys

from telegraph.common import constants


def main():

	try:
		if os.path.isfile(constants.CONFIG_FILE):
			response = input('Config file already exists.  Recreate? [y/N]: ' or 'n')
			if response.lower() != 'y':
				sys.exit()

		serverConfig = {}
		clientConfig = {}
		commonConfig = {}
		serverConfig['WPM'] = input('WPM playback speed [20]: ') or 20
		serverConfig['Port'] = input('Local port [8000]: ') or 8000

		print()
		print("    S: Single contact")
		print("        Configured in this script.")
		print("        To change the destination server you will have to rerun this")
		print("        script and restart your server.")
		print("    M: Multiple contacts")
		print("        Allows sending telegrams to various contacts without")
		print("        restarting the server.")
		print("        Contacts are identified by a callsign that must be sent in the message.")
		destMode = ""
		while destMode != 's' and destMode != 'm':
			destMode = input('Destination mode: ').lower()
		multiDest = destMode == 'm'
		clientConfig['Multiple Destinations'] = multiDest

		if not multiDest:
			clientConfig['Address'] = input('Remote IP address/hostname [localhost]: ') or 'localhost'
			clientConfig['Port'] = input('Remote port [8000]: ') or 8000

		debug = input('Enable debug info [y/N]: ') or 'n'
		commonConfig['Debug'] = debug.lower() == 'y'
		commonConfig['Version'] = constants.CONFIG_FILE_VERSION

	except KeyboardInterrupt:
		sys.exit()

	config = configparser.ConfigParser()
	config['Server'] = serverConfig
	config['Client'] = clientConfig
	config['Common'] = commonConfig

	try:
		with open(constants.CONFIG_FILE, 'w') as configFile:
			config.write(configFile)
	except IOError:
		print("Error: Failed to update " + constants.CONFIG_FILE + ".")
		sys.exit()

	if multiDest:
		print("")
		print("Use `./configureContacts.py` to create contacts and groups.")

if __name__ == '__main__':
	main()

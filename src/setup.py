#! /usr/bin/python3

import configparser
import os.path

def main():
	if os.path.isfile('config.ini'):
		response = input('Config file already exists.  Recreate? [y/N]: ' or 'n')
		if response.lower() != 'y':
			exit()

	serverConfig = {}
	clientConfig = {}
	serverConfig['WPM'] = input('WPM playback speed [20]: ') or 20
	serverConfig['Port'] = input('Local port [8000]: ') or 8000
	clientConfig['Address'] = input('Remote IP address/hostname: ')
	clientConfig['Port'] = input('Remote port [8000]: ') or 8000

	config = configparser.ConfigParser()
	config['Server'] = serverConfig
	config['Client'] = clientConfig
	with open('config.ini', 'w') as configFile:
		config.write(configFile)
		print('Setup complete.')

if __name__ == '__main__':
	main()
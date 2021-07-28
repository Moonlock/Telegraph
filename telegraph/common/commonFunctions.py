import configparser
import sys

from telegraph.common import constants
from telegraph.common.symbols import Symbol
from telegraph.learnMorse.alphabet import morse


def fatal(message):
	print("Error: " + message)
	sys.exit()


try:
	config = configparser.ConfigParser()
	config.read(constants.CONFIG_FILE)
	dbgEnabled = config['Common'].getboolean('Debug')
except KeyError:
	fatal("Error reading config file.")


def isDebugEnabled():
	return dbgEnabled

def toMorse(sign):
	signMorse = []
	for char in sign:
		signMorse.extend(morse[char])
		signMorse.append(Symbol.CHAR_SPACE)

	# Remove trailing character space
	signMorse = signMorse[:-1]
	return "".join([str(int(m)) for m in signMorse])

def writeConfig(filename, parser):
	try:
		with open(filename, 'w') as configFile:
			parser.write(configFile)
	except IOError:
		fatal("Failed to update " + filename + ".")

	print("Updated " + filename + ".")


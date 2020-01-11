import configparser
import sys

from src import constants
from src.learnMorse.alphabet import morse
from src.symbols import Symbol


config = configparser.ConfigParser()
config.read(constants.CONFIG_FILE)
dbgEnabled = config['Common'].getboolean('Debug')

def debug(message):
	if dbgEnabled:
		print(message)

def fatal(message=""):
	print(message)
	sys.exit()

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
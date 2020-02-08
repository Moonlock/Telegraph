import configparser
import glob
import os
import subprocess
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

# sox fails if given too many files, so build final file in chunks
def createFile(fileList, filename):
	partialFile = ""
	for i in range((len(fileList) + 999) // 1000):
		start = i * 1000
		end = (i+1) * 1000

		oldPartialFile = partialFile
		partialFile = constants.SOUND_FILES_PATH + "temp-{}.sox".format(i)
		files = fileList[start:end]

		command = ['sox']
		if oldPartialFile:
			command.append(oldPartialFile)
		command.extend(files)
		command.append(partialFile)
		subprocess.call(command)

	os.rename(partialFile, filename)
	deleteFiles(constants.SOUND_FILES_PATH, "temp-", ".sox")

def deleteFiles(path, prefix="", suffix=""):
	files = glob.glob(path + prefix + "*" + suffix)
	for file in files:
		try:
			os.remove(file)
		except:
			print("Failed to delete " + file)


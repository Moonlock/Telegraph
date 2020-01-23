import configparser
import os
import unittest

from src import commonFunctions
from src.symbols import Symbol as s


class Test(unittest.TestCase):


	def testToMorse(self):
		callsign = "MOON"
		expectedMorse = [s.DAH, s.DAH, s.CHAR_SPACE,
						s.DAH, s.DAH, s.DAH, s.CHAR_SPACE,
						s.DAH, s.DAH, s.DAH, s.CHAR_SPACE,
						s.DAH, s.DIT]

		morseString = commonFunctions.toMorse(callsign)
		calculatedMorse = [s(int(val)) for val in morseString]
		self.assertEqual(expectedMorse, calculatedMorse)

	def testWriteConfig(self):
		section = "Section"
		key = "key"
		expectedValue = "value"
		filename = "testConfig"

		configBefore = configparser.ConfigParser()
		configBefore.read(filename)
		self.assertFalse(configBefore.has_option(section, key))
		configBefore[section] = {key: expectedValue}

		commonFunctions.writeConfig(filename, configBefore)

		configAfter = configparser.ConfigParser()
		configAfter.read(filename)
		self.assertTrue(configAfter.has_option(section, key))
		self.assertEqual(expectedValue, configAfter[section][key])

		os.remove(filename)


if __name__ == "__main__":
	unittest.main()
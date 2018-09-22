#! /usr/bin/python3
import sys
from learnMorse import learnMorse

DEFAULT_CHAR_WPM = 20
DEFAULT_OVERALL_WPM = 10
DEFAULT_NUM_CHARS = 2
DEFAULT_TEST_TIME = 300

charWpm = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CHAR_WPM
overallWpm = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OVERALL_WPM
numChars = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_NUM_CHARS
testTime = int(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_TEST_TIME

learnMorse.morseTest(charWpm, overallWpm, numChars, testTime)

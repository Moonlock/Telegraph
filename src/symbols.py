from enum import IntEnum

class Symbol(IntEnum):
	CHAR_SPACE = 0
	WORD_SPACE = 1
	DIT = 2
	DAH = 3

	def isChar(self):
		return self.value >= 2

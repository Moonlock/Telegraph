from unittest import mock
import unittest

from src.symbols import Symbol as s
from src.telegraph.client import Client
from src.telegraph.destinationConfig import DestinationConfig


DIT = 0.060
DAH = 3*DIT

SYM_SPACE = DIT
CHAR_SPACE = 3*DIT
WORD_SPACE = 7*DIT

INIT_MESSAGE = [s.DAH, s.DIT, s.DAH, s.DIT, s.DAH]


class TestSingleDestination(unittest.TestCase):

	def setUp(self):
		self.client = Client(False, '1.1.1.1', '8000', None, True)


	@mock.patch('src.telegraph.client.time')
	def testInitSequence(self, mock_time):
		self.assertFalse(self.client.message)

		mock_time.return_value = 0
		init = [SYM_SPACE, DAH, SYM_SPACE, DIT, SYM_SPACE, DAH, SYM_SPACE, DIT, SYM_SPACE, DAH]
		inputSequence(init, self.client.initHandlePress, self.client.initHandleRelease, mock_time)

		self.assertEqual(DIT*1000, self.client.timeUnit)
		self.assertEqual(INIT_MESSAGE, self.client.message)

	@mock.patch('src.telegraph.client.time')
	@mock.patch('src.telegraph.client.socket')
	def testSend(self, mock_socket, mock_time):
		self.client.message = []
		self.client.message.extend(INIT_MESSAGE)
		self.client.timeUnit = DIT*1000

		mock_time.return_value = 0
		end = [WORD_SPACE, DIT, SYM_SPACE, DAH, SYM_SPACE, DIT, SYM_SPACE, DAH, SYM_SPACE, DIT]
		inputSequence(end, self.client.handlePress, self.client.handleRelease, mock_time)

		instance = mock_socket.socket.return_value
		instance.connect.assert_called_with(('1.1.1.1', '8000'))
		self.assertTrue(instance.sendall.called)


class TestMultipleDestinations(unittest.TestCase):

	def setUp(self):
		self.client = Client(True, None, None, None, True)
		self.client.destConfig = DestinationConfig(self.client.callSignError,
				"test/telegraph/testContacts.ini", "test/telegraph/testGroups.ini")

		self.moonlockEndpoint = ('1.1.1.1', '8000')
		self.muskratEndpoint = ('2.2.2.2', '8001')


	@mock.patch('src.telegraph.client.time')
	def testParseCallsign(self, mock_time):
		self.client.message = []
		self.client.message.extend(INIT_MESSAGE)
		self.client.timeUnit = DIT*1000

		mock_time.return_value = 0
		callsign = [WORD_SPACE, DAH, SYM_SPACE, DAH, CHAR_SPACE,
			DAH, SYM_SPACE, DAH, SYM_SPACE, DAH, CHAR_SPACE,
			DAH, SYM_SPACE, DAH, SYM_SPACE, DAH, CHAR_SPACE,
			DAH, SYM_SPACE, DIT, WORD_SPACE]

		inputSequence(callsign, self.client.handlePress, self.client.handleRelease, mock_time)
		self.assertEqual([self.moonlockEndpoint], self.client.dests)

	@mock.patch('src.telegraph.client.time')
	def testIncorrectCallsignCancelsMessage(self, mock_time):
		self.client.message = []
		self.client.message.extend(INIT_MESSAGE)
		self.client.timeUnit = DIT*1000

		mock_time.return_value = 0
		callsign = [WORD_SPACE, DAH, SYM_SPACE, DAH, WORD_SPACE]

		inputSequence(callsign, self.client.handlePress, self.client.handleRelease, mock_time)
		self.assertEqual([], self.client.dests)
		self.assertEqual([], self.client.message)

	@mock.patch('src.telegraph.client.time')
	@mock.patch('src.telegraph.client.socket')
	def testSendToGroup(self, mock_socket, mock_time):
		self.client.message = []
		self.client.message.extend(INIT_MESSAGE)
		self.client.timeUnit = DIT*1000

		mock_time.return_value = 0
		callsign = [WORD_SPACE, DAH, SYM_SPACE, DAH, SYM_SPACE, DIT, CHAR_SPACE,
			DIT, SYM_SPACE, DAH, SYM_SPACE, DIT, CHAR_SPACE,
			DAH, SYM_SPACE, DAH, SYM_SPACE, DAH, CHAR_SPACE,
			DIT, SYM_SPACE, DIT, SYM_SPACE, DAH, CHAR_SPACE,
			DIT, SYM_SPACE, DAH, SYM_SPACE, DAH, SYM_SPACE, DIT, WORD_SPACE]

		inputSequence(callsign, self.client.handlePress, self.client.handleRelease, mock_time)
		self.assertEqual([self.moonlockEndpoint, self.muskratEndpoint], self.client.dests)

		end = [SYM_SPACE, DIT, SYM_SPACE, DAH, SYM_SPACE, DIT, SYM_SPACE, DAH, SYM_SPACE, DIT]
		inputSequence(end, self.client.handlePress, self.client.handleRelease, mock_time)

		instance = mock_socket.socket.return_value
		self.assertEqual(2, instance.connect.call_count)
		self.assertEqual(2, instance.sendall.call_count)
		instance.connect.assert_has_calls([
				mock.call( (self.moonlockEndpoint[0], int(self.moonlockEndpoint[1])) ),
				mock.call( (self.muskratEndpoint[0], int(self.muskratEndpoint[1])) )
		])


def inputSequence(sequence, pressCallback, releaseCallback, mock_time):
	for i in range(len(sequence)//2):
		mock_time.return_value += sequence[2*i]
		pressCallback()
		mock_time.return_value += sequence[2*i + 1]
		releaseCallback()

	if(len(sequence)%2):
		mock_time.return_value += sequence[-1]
		pressCallback()


if __name__ == "__main__":
	unittest.main()


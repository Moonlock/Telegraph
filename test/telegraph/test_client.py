from threading import Event
from unittest import mock
import unittest

from telegraph.client.client import Client
from telegraph.common.clientMode import ClientMode
from telegraph.common.symbols import Symbol as s
from telegraph.destinations.destinationConfig import DestinationConfig


DIT = 60000
DAH = 3*DIT

SYM_SPACE = DIT
CHAR_SPACE = 3*DIT
WORD_SPACE = 7*DIT

INIT_MESSAGE = [s.DAH, s.DIT, s.DAH, s.DIT, s.DAH]


class TestSingleDestination(unittest.TestCase):

	@mock.patch('telegraph.listeners.listenerInterface.ListenerInterface')
	def setUp(self, mock_listener):
		self.mock_listener_instance = mock_listener.instance
		destConfig = DestinationConfig()
		self.client = Client(False, '1.1.1.1', '8000', self.mock_listener_instance, destConfig, None, Event(), True)


	def testInitSequence(self):
		self.assertFalse(self.client.message)

		init = [SYM_SPACE, DAH, SYM_SPACE, DIT, SYM_SPACE, DAH, SYM_SPACE, DIT, SYM_SPACE, DAH]
		inputSequence(init, self.client.initKeyEvent)

		self.assertEqual(DIT, self.client.timeUnitUsec)
		self.assertEqual(INIT_MESSAGE, self.client.message)

		self.mock_listener_instance.setMode.assert_called_with(ClientMode.MAIN)

	@mock.patch('telegraph.client.client.socket')
	def testSend(self, mock_socket):
		self.client.message = []
		self.client.message.extend(INIT_MESSAGE)
		self.client.timeUnitUsec = DIT

		end = [WORD_SPACE, DIT, SYM_SPACE, DAH, SYM_SPACE, DIT, SYM_SPACE, DAH, SYM_SPACE, DIT]
		inputSequence(end, self.client.mainKeyEvent)

		instance = mock_socket.socket.return_value
		instance.connect.assert_called_with(('1.1.1.1', 8000))
		self.assertTrue(instance.sendall.called)
		self.mock_listener_instance.setMode.assert_called_with(ClientMode.INIT)


class TestMultipleDestinations(unittest.TestCase):

	@mock.patch('telegraph.listeners.listenerInterface.ListenerInterface')
	def setUp(self, mock_listener):
		destConfig = DestinationConfig(
				"test/telegraph/testContacts.ini", "test/telegraph/testGroups.ini")
		self.client = Client(True, None, None, mock_listener, destConfig, None, Event(), True)

		self.moonlockEndpoint = ('1.1.1.1', '8000')
		self.muskratEndpoint = ('2.2.2.2', '8001')


	def testParseCallsign(self):
		self.client.message = []
		self.client.message.extend(INIT_MESSAGE)
		self.client.timeUnitUsec = DIT

		callsign = [WORD_SPACE, DAH, SYM_SPACE, DAH, CHAR_SPACE,
			DAH, SYM_SPACE, DAH, SYM_SPACE, DAH, CHAR_SPACE,
			DAH, SYM_SPACE, DAH, SYM_SPACE, DAH, CHAR_SPACE,
			DAH, SYM_SPACE, DIT, WORD_SPACE]

		inputSequence(callsign, self.client.mainKeyEvent)
		self.assertEqual([self.moonlockEndpoint], self.client.dests)

	def testIncorrectCallsignCancelsMessage(self):
		self.client.message = []
		self.client.message.extend(INIT_MESSAGE)
		self.client.timeUnitUsec = DIT

		callsign = [WORD_SPACE, DAH, SYM_SPACE, DAH, WORD_SPACE]

		inputSequence(callsign, self.client.mainKeyEvent)
		self.assertIsNone(self.client.dests)
		self.assertEqual([], self.client.message)

	@mock.patch('telegraph.client.client.socket')
	def testSendToGroup(self, mock_socket):
		self.client.message = []
		self.client.message.extend(INIT_MESSAGE)
		self.client.timeUnitUsec = DIT

		callsign = [WORD_SPACE, DAH, SYM_SPACE, DAH, SYM_SPACE, DIT, CHAR_SPACE,
			DIT, SYM_SPACE, DAH, SYM_SPACE, DIT, CHAR_SPACE,
			DAH, SYM_SPACE, DAH, SYM_SPACE, DAH, CHAR_SPACE,
			DIT, SYM_SPACE, DIT, SYM_SPACE, DAH, CHAR_SPACE,
			DIT, SYM_SPACE, DAH, SYM_SPACE, DAH, SYM_SPACE, DIT, WORD_SPACE]

		inputSequence(callsign, self.client.mainKeyEvent)
		self.assertEqual([self.moonlockEndpoint, self.muskratEndpoint], self.client.dests)

		end = [SYM_SPACE, DIT, SYM_SPACE, DAH, SYM_SPACE, DIT, SYM_SPACE, DAH, SYM_SPACE, DIT]
		inputSequence(end, self.client.mainKeyEvent)

		instance = mock_socket.socket.return_value
		self.assertEqual(2, instance.connect.call_count)
		self.assertEqual(2, instance.sendall.call_count)
		instance.connect.assert_has_calls([
				mock.call( (self.moonlockEndpoint[0], int(self.moonlockEndpoint[1])) ),
				mock.call( (self.muskratEndpoint[0], int(self.muskratEndpoint[1])) )
		])


def inputSequence(sequence, modeCallback):
	for i in range(len(sequence)//2):
		modeCallback(True, sequence[2*i])
		modeCallback(False, sequence[2*i + 1])

	if(len(sequence)%2):
		modeCallback(True, sequence[-1])


if __name__ == "__main__":
	unittest.main()


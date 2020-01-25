import os
import unittest

from src.telegraph.destinationConfig import DestinationConfig
import src.commonFunctions as common


TEST_CONTACTS_FILE = "testContactsFile"
TEST_GROUPS_FILE = "testGroupsFile"

class TestNormalOperation(unittest.TestCase):

	def setUp(self):
		self.moonlock = {"Name": "Moonlock",
				"Sign": "MOON",
				"Address": "1.1.1.1",
				"Port": "8000"}

		self.muskrat = {"Name": "Muskrat",
				"Sign": "MUSK",
				"Address": "2.2.2.2",
				"Port": "8001"}

		self.group = {"Name": "Group",
				"Sign": "GROUP",
				"Members": str(common.toMorse(self.moonlock["Sign"])) + " " +
						str(common.toMorse(self.muskrat["Sign"]))}

		self.destinationConfig = DestinationConfig(self.error, TEST_CONTACTS_FILE, TEST_GROUPS_FILE)

	def tearDown(self):
		if os.path.exists(TEST_CONTACTS_FILE):
			os.remove(TEST_CONTACTS_FILE)
		if os.path.exists(TEST_GROUPS_FILE):
			os.remove(TEST_GROUPS_FILE)


	def testAddContact(self):
		self.destinationConfig.addContact(self.moonlock)
		retrievedContact = self.destinationConfig.createDestination(common.toMorse(self.moonlock["Sign"]))

		expectedEndpoints = [(self.moonlock["Address"], self.moonlock["Port"])]

		self.assertEqual(self.moonlock["Name"], retrievedContact.getName())
		self.assertEqual(self.moonlock["Sign"], retrievedContact.getSign())
		self.assertEqual(expectedEndpoints, retrievedContact.getEndpoints())

	def testAddGroup(self):
		self.destinationConfig.addContact(self.moonlock)
		self.destinationConfig.addContact(self.muskrat)
		self.destinationConfig.addGroup(self.group)
		retrievedGroup = self.destinationConfig.createDestination(common.toMorse(self.group["Sign"]))

		expectedEndpoints = [(self.moonlock["Address"], self.moonlock["Port"]),
							(self.muskrat["Address"], self.muskrat["Port"])]

		self.assertEqual(self.group["Name"], retrievedGroup.getName())
		self.assertEqual(self.group["Sign"], retrievedGroup.getSign())
		self.assertEqual([self.moonlock["Sign"], self.muskrat["Sign"]], retrievedGroup.getMemberCallsigns())
		self.assertEqual(expectedEndpoints, retrievedGroup.getEndpoints())

	def testGetAllDests(self):
		self.destinationConfig.addContact(self.moonlock)
		self.destinationConfig.addContact(self.muskrat)
		self.destinationConfig.addGroup(self.group)

		contacts = self.destinationConfig.getAllContacts()
		groups = self.destinationConfig.getAllGroups()

		self.assertEqual(2, len(contacts))
		self.assertEqual(1, len(groups))
		self.assertIn(self.moonlock['Name'], [contact.getName() for contact in contacts])
		self.assertIn(self.muskrat['Name'], [contact.getName() for contact in contacts])
		self.assertIn(self.group["Name"], groups[0].getName())

	def error(self, message):
		self.assertTrue(False)


class TestError(unittest.TestCase):

	class ExpectedError(Exception):
		pass

	def testCallsignDoesNotExist(self):
		destinationConfig = DestinationConfig(self.error, TEST_CONTACTS_FILE, TEST_GROUPS_FILE)

		with self.assertRaises(self.ExpectedError):
			destinationConfig.createDestination(common.toMorse("TEST"))

	def error(self, message):
		raise self.ExpectedError


if __name__ == "__main__":
	unittest.main()
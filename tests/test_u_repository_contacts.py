import unittest
from unittest.mock import MagicMock, AsyncMock, Mock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from entity.models import Contact, User
from schemas.contacts import ContactSchema, ContactUpdateSchema, ContactResponseSchema
from repository.contacts import create_contact, get_contact, get_contacts, update_contact, delete_contact, \
    get_contact_by_email, get_contact_by_phone, search_contacts, get_birthdays

from fastapi import HTTPException
from conf import messages


class TestAsyncContact(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = User(id=1, username='user', password='12345678', email='user@example.com', confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1,
                            first_name='name1',
                            last_name='lname1',
                            email='user1@example.com',
                            phone='111111111',
                            notes='notes1'),
                    Contact(id=2,
                            first_name='name2',
                            last_name='lname2',
                            email='user2@example.com',
                            phone='222222222',
                            notes='notes2')]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEquals(result, contacts)

    async def create_contact(self):
        body = ContactSchema(first_name='name1', last_name='lname1', email='user1@example.com',
                             phone='111111111', notes='notes1')
        # result = await create_contact(body, self.session, self.user)
        with patch(
                'repository.contacts.create_contact') as mocked_create_contact:
            result = await create_contact(body, self.session, self.user)

        mocked_create_contact.assert_called_once_with(body, self.session, self.user)

        self.assertIsInstance(result, Contact)
        self.assertEquals(result.first_name, body.first_name)
        self.assertEquals(result.last_name, body.last_name)
        self.assertEquals(result.email, body.email)
        self.assertEquals(result.phone, body.phone)
        self.assertEquals(result.notes, body.notes)
        self.session.commit.assert_called()
        self.session.refresh.assert_called()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()

    async def test_update_contact(self):
        body = ContactUpdateSchema(first_name='name1', last_name='lname1', email='user1@example.com',
                                   phone='111111111', notes='notes1')
        mocked_contact = MagicMock()
        mocked_contact.scalars_or_none.return_value = Contact(id=1, first_name='name1', last_name='lname1',
                                                              email='user1@example.com',
                                                              phone='111111111', notes='notes1')
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.assertEquals(result.first_name, body.first_name)
        self.assertEquals(result.last_name, body.last_name)
        self.assertEquals(result.email, body.email)
        self.assertEquals(result.phone, body.phone)
        self.assertEquals(result.notes, body.notes)
        self.session.commit.assert_called_once()

    async def test_update_not_existed_contact(self):
        """
        Test update_contact with not existed contact id
        and check if it raises HTTPException with 404 status code and 'Contact not found' message
        """
        body = ContactUpdateSchema(first_name='name1', last_name='lname1', email='user1@example.com',
                                   phone='111111111', notes='notes1')

        mocked_update_contact = MagicMock(side_effect=HTTPException(status_code=404, detail="Contact not found"))

        self.session.execute.return_value = mocked_update_contact
        self.session.execute.return_value.scalar_one_or_none.return_value = None

        with patch('repository.contacts.update_contact', mocked_update_contact) as mock_update_contact:
            with self.assertRaises(HTTPException) as context:
                result = await update_contact(100, body, self.session, self.user)

            self.assertEqual(context.exception.status_code, 404)
            self.assertEqual(context.exception.detail, messages.CONTACT_NOT_FOUND)

    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalars_or_none.return_value = Contact(id=1, first_name='name1', last_name='lname1',
                                                              email='user1@example.com',
                                                              phone='111111111', notes='notes1')
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        # self.assertIsInstance(result, Contact)
        self.session.delete.assert_called_once()

    async def test_delete_not_existed_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalars_or_none.return_value = None
        self.session.execute.return_value = mocked_contact
        self.session.execute.return_value.scalar_one_or_none.return_value = None
        result = await delete_contact(100, self.session, self.user)
        self.assertIsNone(result)

    async def test_get_contact(self):
        contact_id = 1
        expected_contact = Contact(id=contact_id, first_name='name1', last_name='lname1', user=self.user)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = expected_contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(contact_id, self.session, self.user)
        self.assertEqual(result, expected_contact)

    async def test_get_contact_not_exist(self):
        contact_id = 10
        expected_contact = None
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = expected_contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(contact_id, self.session, self.user)
        self.assertEqual(result, expected_contact)

    async def test_get_contact_by_email(self):
        email = 'user1@example.com'
        expected_contact = Contact(id=1, first_name='name1', last_name='lname1', user=self.user)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = expected_contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact_by_email(email, self.session, self.user)
        self.assertEqual(result, expected_contact)

    async def test_get_contact_by_phone(self):
        phone = '111111111'
        expected_contact = Contact(id=1, first_name='name1', last_name='lname1', user=self.user)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = expected_contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact_by_phone(phone, self.session, self.user)
        self.assertEqual(result, expected_contact)

    async def test_search_contacts(self):
        limit = 10
        offset = 0
        query = 'name1'
        contacts = [Contact(id=1,
                            first_name='name1',
                            last_name='lname1',
                            email='user1@example.com',
                            phone='111111111',
                            notes='notes1'),
                    Contact(id=2,
                            first_name='name2',
                            last_name='lname2',
                            email='user2@example.com',
                            phone='222222222',
                            notes='notes2')]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await search_contacts(limit, offset, query, self.session, self.user)
        self.assertEquals(result, contacts)

    async def test_search_not_existed_contacts(self):
        limit = 10
        offset = 0
        query = 'name1111'
        contacts = []
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await search_contacts(limit, offset, query, self.session, self.user)
        self.assertEquals(result, contacts)

    async def test_get_birthdays(self):
        contacts = [Contact(id=1,
                            first_name='name1',
                            last_name='lname1',
                            email='user1@example.com',
                            phone='111111111',
                            notes='notes1',
                            birthday='2022-01-01'),
                    Contact(id=2,
                            first_name='name2',
                            last_name='lname2',
                            email='user2@example.com',
                            phone='222222222',
                            notes='notes2',
                            birthday='2022-02-02')]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_birthdays(self.session, self.user)
        self.assertEquals(result, contacts)

    async def test_get_birthdays_no_contacts_return(self):
        contacts = []
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_birthdays(self.session, self.user)
        self.assertEquals(result, contacts)

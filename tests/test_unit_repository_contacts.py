import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactResponse, ContactUpdate
from src.repository.contacts import (
    get_contacts, 
    create_contact,
    get_contact, 
    update_contact, 
    remove_contact, 
    get_contacts_with_name, 
    get_contacts_with_lastname, 
    get_contacts_with_email, 
    get_contacts_with_recent_birthdays,
    has_birthday_next_week
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    
    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all = contacts
        result = await get_contacts(db=self.session, user=self.user)
        self.assertEqual(result, contacts)


    async def test_get_contact(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, db=self.session, user=self.user)
        self.assertEqual(result, contact)


    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, db=self.session, user=self.user)
        self.assertIsNone(result)


    async def test_create_contact(self):
        body = ContactModel(firstname='Jane',
                            lastname='Dou',
                            email='jd@mail.com',
                            phone='08897656456',
                            birthday="2000-10-31",
                            user_id=self.user.id)
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.lastname, body.lastname)
        self.assertEqual(result.email, body.email)
        self.assertTrue(hasattr(result, "id"))


    async def test_update_contact(self):
        body = ContactModel(firstname='Jane',
                            lastname='Dou',
                            email='jd@mail.com',
                            phone='08897656455',
                            birthday="2000-10-31",
                            user_id=self.user.id)
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_update_note_not_found(self):
        body = ContactUpdate(firstname='Jane',
                             lastname='Dou',
                             email='jdou@mail.com',
                             phone='08877777777',
                             birthday="2000-10-31")
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)


    async def test_remove_contact(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_remove_note_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    
    async def test_get_contacts_with_name(self):
        name='Jane'
        contacts = [Contact(firstname=name), Contact(firstname=name), Contact(firstname=name)]
        self.session.query().filter().all = contacts
        result = await get_contacts_with_name(db=self.session, name=name, user=self.user)
        self.assertEqual(result, contacts)


    async def test_get_contacts_with_lasname(self):
        lastname='Dou'
        contacts = [Contact(lastname=lastname), Contact(lastname=lastname), Contact(lastname=lastname)]
        self.session.query().filter().all = contacts
        result = await get_contacts_with_lastname(db=self.session, lastname=lastname, user=self.user)
        self.assertEqual(result, contacts)


    async def test_get_contacts_with_email(self):
        email='dou@mail.com'
        contacts = [Contact(email=email), Contact(email=email), Contact(email=email)]
        self.session.query().filter().all = contacts
        result = await get_contacts_with_email(db=self.session, email=email, user=self.user)
        self.assertEqual(result, contacts)


    async def test_get_contacts_with_recent_birthdays(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all = contacts
        result = await get_contacts_with_recent_birthdays(db=self.session, user=self.user)
        self.assertEqual(result, contacts)


if __name__ == '__main__':
    unittest.main()


import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import UserDb, UserModel, UserResponse
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)


    async def test_get_users(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(db=self.session, email='test@mail.com')
        self.assertEqual(result, user)


    async def test_create_user(self):
        body = UserModel(username='testname',
                         email='jd@mail.com',
                         password='654321')
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    
    async def test_update_token(self):
        self.session.commit.return_value = None
        result = await update_token(user=self.user, token='test_token', db=self.session)
        self.assertIsNone(result)


    async def test_confirmed_email(self):
        self.session.commit.return_value = None
        result = await confirmed_email(email='test@mail.com', db=self.session)
        self.assertIsNone(result)


    async def test_update_avatar(self):
        user = User()
        self.session.query().filter().first.return_value = user
        self.session.commit.return_value = user
        result = await update_avatar(email='test@mail.com', url='test_url', db=self.session)
        self.assertEqual(result, user)

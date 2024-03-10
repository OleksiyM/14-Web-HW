import unittest
from unittest.mock import MagicMock, AsyncMock, Mock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from entity.models import User
from schemas.users import UserSchema, UserResponse, TokenSchema, RequestEmail
from repository.users import update_token, create_user, get_user_by_email, get_user_by_username, confirmed_email, \
    update_avatar_url


class TestAsyncUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=1, username='user', password='12345678', email='user@example.com', confirmed=True)
        self.new_token = 'updated_token'
        self.new_avatar_url = 'https://new-avatar.com/image.jpg'
        self.contact = {
            "first_name": "Jack",
            "last_name": "Smith",
            "email": "jack@example.com",
            "birthday": "2000-01-01",
            "phone": "1234567890",
            "notes": "user 1 notes"
        }
        self.session = AsyncMock(spec=AsyncSession)

    async def test_update_token(self):
        mocked_user = MagicMock()
        mocked_user.scalars_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user
        result = await update_token(self.user, self.new_token, self.session)
        self.assertIsNone(result)
        self.session.commit.assert_called_once()

    async def test_create_user(self):
        body = UserSchema(username='user', password='12345678', email='user@example.com')
        result = await create_user(body, self.session)
        self.assertIsInstance(result, User)
        self.assertEquals(result.username, 'user')
        self.assertEquals(result.password, '12345678')
        self.assertEquals(result.email, 'user@example.com')
        self.assertIsNotNone(result.avatar)
        self.session.commit.assert_called_once()

    async def test_get_user_by_email(self):
        """Tests if get_user_by_email retrieves a user by email."""
        self.session.execute.return_value.scalar_one_or_none.return_value = self.user
        existing_email = "user@example.com"
        user = await get_user_by_email(existing_email, self.session)
        user = await user
        self.assertEqual(user.username, self.user.username)
        self.assertEqual(user.email, self.user.email)
        self.assertEqual(user.confirmed, self.user.confirmed)

    async def test_get_non_existing_user_by_email(self):
        """Tests if get_user_by_email retrieves a not existing user by email."""
        existing_email = "user@example.com"
        # Test case with non-existent user
        self.session.execute.return_value.scalar_one_or_none.return_value = None
        user = await get_user_by_email(existing_email, self.session)
        user = await user
        self.assertIsNone(user)

    async def test_get_user_by_not_existing_email(self):
        """Tests if get_user_by_email retrieves a user by not existing email."""
        self.session.execute.return_value.scalar_one_or_none.return_value = self.user
        not_existing_email = "not_existing_user@example.com"
        # Test case with non-existent email
        self.session.execute.return_value.scalar_one_or_none.return_value = None
        user = await get_user_by_email(not_existing_email, self.session)
        user = await user
        self.assertIsNone(user)

    async def test_get_user_by_username(self):
        self.session.execute.return_value.scalar_one_or_none.return_value = self.user
        existing_user = "user"
        user = await get_user_by_username(existing_user, self.session)
        user = await user
        self.assertEqual(user.username, self.user.username)
        self.assertEqual(user.email, self.user.email)
        self.assertEqual(user.confirmed, self.user.confirmed)

    async def test_get_non_existing_user_by_username(self):
        existing_user = "user"
        # Test case with non-existent user
        self.session.execute.return_value.scalar_one_or_none.return_value = None
        user = await get_user_by_username(existing_user, self.session)
        user = await user
        self.assertIsNone(user)

    async def test_get_user_by_not_existing_username(self):
        self.session.execute.return_value.scalar_one_or_none.return_value = self.user
        not_existing_user = "not_existing_user"
        self.session.execute.return_value.scalar_one_or_none.return_value = None
        user = await get_user_by_email(not_existing_user, self.session)
        user = await user
        self.assertIsNone(user)

    async def test_confirmed_email(self):
        """Tests if confirmed_email marks a user as confirmed."""
        mocked_get_user_by_email = AsyncMock(return_value=self.user)
        self.session.execute.return_value = mocked_get_user_by_email

        mocked_get_user_by_email.return_value = User(
            id=1, username='user', password='12345678', email='user@example.com', confirmed=False
        )
        self.session.execute.return_value = mocked_get_user_by_email
        with patch('repository.users.get_user_by_email', mocked_get_user_by_email):
            result = await confirmed_email('user@example.com', self.session)

            self.session.commit.assert_called_once()
            self.session.refresh.assert_not_called()

    async def test_update_avatar_url_success(self):
        """Tests successful update of avatar URL."""
        mocked_get_user_by_email = AsyncMock(return_value=self.user)
        self.session.execute.return_value = mocked_get_user_by_email
        mocked_get_user_by_email.return_value = self.user
        self.session.execute.return_value = mocked_get_user_by_email

        with patch('repository.users.get_user_by_email', mocked_get_user_by_email):
            updated_user = await update_avatar_url(self.user.email, self.new_avatar_url, self.session)

        self.assertIsInstance(updated_user, User)
        self.assertEqual(updated_user.avatar, self.new_avatar_url)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()

    async def test_update_avatar_url_user_not_found(self):
        """Tests update_avatar_url behavior when the user is not found."""
        self.session.execute.return_value.scalar_one_or_none.return_value = None

        with self.assertRaises(Exception):
            await update_avatar_url(self.user.email, self.session)
            await update_avatar_url(self.user.email, self.new_avatar_url, self.session)

        self.session.commit.assert_not_called()
        self.session.refresh.assert_not_called()

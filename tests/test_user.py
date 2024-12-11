import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.models.user import User, Role

from src.schemas.user import CreateUserRequest, LoginRequest, UpdateEmailRequest, UpdateUserRequest, UserResponse
from src.crud.users import (is_admin, is_director, username_exists,
                            email_exists, create_user, login_user,
                            get_user_by_id, update_email, delete_user)
from src.common.custom_responses import AlreadyExists, NotFound, Unauthorized, ForbiddenAccess, BadRequest


class UserCRUDShould(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.current_user = User(id=uuid4(), username="test_user", password="password123!",
                                 email="test@example.com", role=Role.ADMIN)
        self.db.query.return_value.filter.return_value.first.return_value = None

    def test_is_admin(self):
        self.assertTrue(is_admin(self.current_user))
        self.current_user.role = Role.USER
        self.assertFalse(is_admin(self.current_user))

    def test_is_director(self):
        self.current_user.role = Role.DIRECTOR
        self.assertTrue(is_director(self.current_user))
        self.current_user.role = Role.USER
        self.assertFalse(is_director(self.current_user))

    def test_username_exists(self):
        self.db.query.return_value.filter.return_value.first.return_value = self.current_user
        self.assertTrue(username_exists(self.db, "test_user"))
        self.db.query.return_value.filter.return_value.first.return_value = None
        self.assertFalse(username_exists(self.db, "nonexistent_user"))

    def test_email_exists(self):
        self.db.query.return_value.filter.return_value.first.return_value = self.current_user
        self.assertTrue(email_exists(self.db, "test@example.com"))
        self.db.query.return_value.filter.return_value.first.return_value = None
        self.assertFalse(email_exists(self.db, "nonexistent@example.com"))

    def test_create_user_success(self):
        user_request = CreateUserRequest(username="new_user", email="new@example.com", password="password123!")
        self.db.query.return_value.filter.return_value.first.return_value = None
        response = create_user(self.db, user_request)
        self.assertEqual(response, "Registration was successfully completed")

    def test_create_user_username_exists(self):
        user_request = CreateUserRequest(username="existing_user", email="new@example.com", password="password123!")
        self.db.query.return_value.filter.return_value.first.side_effect = [self.current_user, None]
        response = create_user(self.db, user_request)
        self.assertIsInstance(response, AlreadyExists)

    def test_login_user_success(self):
        login_request = LoginRequest(username="test_user", password="password123!")
        self.db.query.return_value.filter.return_value.first.return_value = self.current_user
        with patch("src.crud.users.verify_password", return_value=True) as mock_verify_password, \
             patch("src.crud.users.username_exists", return_value=True), \
             patch("src.crud.users.create_access_token", return_value="token") as mock_create_access_token:
            token = login_user(self.db, login_request)
            self.assertEqual(token, "token")
            mock_verify_password.assert_called_once_with("password123!", self.current_user.password)
            mock_create_access_token.assert_called_once_with(self.current_user)

    def test_login_user_failure(self):
        login_request = LoginRequest(username="nonexistent_user", password="password123!")
        self.db.query.return_value.filter.return_value.first.return_value = None
        response = login_user(self.db, login_request)
        self.assertIsInstance(response, Unauthorized)

    def test_get_user_by_id_success(self):
        self.db.query.return_value.filter.return_value.first.return_value = self.current_user
        response = get_user_by_id(self.db, self.current_user.id, self.current_user)
        self.assertIsInstance(response, UserResponse)

    def test_get_user_by_id_not_found(self):
        self.db.query.return_value.filter.return_value.first.return_value = None
        response = get_user_by_id(self.db, uuid4(), self.current_user)
        self.assertIsInstance(response, NotFound)

    def test_update_email_success(self):
        new_email_request = UpdateEmailRequest(email="updated@example.com")
        self.db.query.return_value.filter.return_value.first.return_value = None
        response = update_email(self.db, new_email_request, self.current_user)
        self.assertIsInstance(response, UserResponse)
        self.assertEqual(response.email, "updated@example.com")

    def test_update_email_already_exists(self):
        new_email_request = UpdateEmailRequest(email="existing@example.com")
        self.db.query.return_value.filter.return_value.first.return_value = self.current_user
        response = update_email(self.db, new_email_request, self.current_user)
        self.assertIsInstance(response, AlreadyExists)

    def test_delete_user_success(self):
        self.db.query.return_value.filter.return_value.first.return_value = self.current_user
        response = delete_user(self.db, self.current_user.username, self.current_user)
        self.assertEqual(response, f"User {self.current_user.username} successfully deleted")

    def test_delete_user_not_found(self):
        self.db.query.return_value.filter.return_value.first.return_value = None
        response = delete_user(self.db, "nonexistent_user", self.current_user)
        self.assertIsInstance(response, NotFound)


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import MagicMock
from uuid import uuid4
from src.models.request import RequestType, RequestAction, Requests
from src.models.user import User, Role
from src.models.player import Player
from src.schemas.request import CreateRequest, RequestResponse
from src.crud.requests import creating_request, view_requests, open_request, accept_request, reject_request
from src.common.custom_responses import Unauthorized, NotFound, BadRequest, ForbiddenAccess


class RequestCRUDShould(unittest.TestCase):

    def setUp(self):

        self.db = MagicMock()

        self.mock_user = MagicMock(spec=User)
        self.mock_user.id = 1
        self.mock_user.username = "test_user"
        self.mock_user.role = Role.USER

        self.mock_player = MagicMock(spec=Player)
        self.mock_player.id = 1
        self.mock_player.first_name = "John"
        self.mock_player.last_name = "Doe"

        self.mock_request = CreateRequest(reason="John Doe")

    def test_creating_request_unauthorized(self):

        current_user = None
        response = creating_request(self.db, self.mock_request, current_user, RequestType.PROMOTE)
        self.assertIsInstance(response, Unauthorized)

    def test_creating_request_when_admin(self):

        current_user = self.mock_user
        current_user.role = Role.ADMIN
        response = creating_request(self.db, self.mock_request, current_user, RequestType.PROMOTE)
        self.assertIsInstance(response, BadRequest)
        self.assertEqual(response.content, "Admins cannot make requests")

    def test_creating_promote_request_when_already_director(self):

        current_user = self.mock_user
        current_user.role = Role.DIRECTOR
        response = creating_request(self.db, self.mock_request, current_user, RequestType.PROMOTE)
        self.assertIsInstance(response, BadRequest)

    def test_creating_demote_request_when_user(self):

        current_user = self.mock_user
        current_user.role = Role.USER
        response = creating_request(self.db, self.mock_request, current_user, RequestType.DEMOTE)
        self.assertIsInstance(response, BadRequest)
        self.assertEqual(response.content, "There is no role to demote to")

    def test_creating_link_request_when_already_linked(self):

        current_user = self.mock_user
        mock_player = self.mock_player
        self.db.query.return_value.filter.return_value.first.return_value = mock_player
        response = creating_request(self.db, self.mock_request, current_user, RequestType.LINK)
        self.assertIsInstance(response, BadRequest)
        self.assertEqual(response.content, "You are already linked to a player")

    def test_creating_link_request_invalid_reason(self):

        current_user = self.mock_user
        self.mock_request.reason = "JohnDoe"
        self.db.query.return_value.filter.return_value.first.return_value = None
        response = creating_request(self.db, self.mock_request, current_user, RequestType.LINK)
        self.assertIsInstance(response, BadRequest)
        self.assertEqual(response.content, "Invalid player name format")

    def test_creating_link_request_player_not_found(self):

        current_user = self.mock_user
        self.db.query.return_value.filter.return_value.first.return_value = None
        response = creating_request(self.db, self.mock_request, current_user, RequestType.LINK)
        self.assertIsInstance(response, NotFound)

    def test_creating_unlink_request_when_not_linked(self):

        current_user = self.mock_user
        self.db.query.return_value.filter.return_value.first.return_value = None
        response = creating_request(self.db, self.mock_request, current_user, RequestType.UNLINK)
        self.assertIsInstance(response, BadRequest)
        self.assertEqual(response.content, "You are not linked to any player")

    def test_creating_promote_request_success(self):  # TODO: Create tests for creating all request types
        pass

    def test_view_requests_unauthorized(self):

        current_user = None
        response = view_requests(self.db, current_user, None)
        self.assertIsInstance(response, Unauthorized)

    def test_view_requests_forbidden(self):

        current_user = self.mock_user
        response = view_requests(self.db, current_user, None)
        self.assertIsInstance(response, ForbiddenAccess)

    def test_view_requests_not_found(self):

        current_user = self.mock_user
        current_user.role = Role.ADMIN
        self.db.query.return_value.all.return_value = []
        response = view_requests(self.db, current_user, None)
        self.assertIsInstance(response, NotFound)

    def test_open_request_unauthorized(self):

        current_user = None
        response = open_request(self.db, uuid4(), current_user, RequestAction.ACCEPT)
        self.assertIsInstance(response, Unauthorized)

    def test_open_request_forbidden(self):

        current_user = self.mock_user
        response = open_request(self.db, uuid4(), current_user, RequestAction.ACCEPT)
        self.assertIsInstance(response, ForbiddenAccess)

    def test_open_request_not_found(self):
        current_user = self.mock_user
        current_user.role = Role.ADMIN
        self.db.query.return_value.filter.return_value.first.return_value = None
        response = open_request(self.db, uuid4(), current_user, RequestAction.ACCEPT)
        self.assertIsInstance(response, NotFound)

    def test_accept_request_success(self):
        request = MagicMock(spec=Requests)
        request.type = RequestType.PROMOTE
        request.user_id = 1
        mock_user = self.mock_user
        mock_user.username = "test_user"
        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        response = accept_request(self.db, request)
        self.assertEqual(response, f"{request.type.value} from {mock_user.username} accepted")

    def test_reject_request_success(self):
        request = MagicMock(spec=Requests)
        request.type = RequestType.PROMOTE
        request.user_id = 1
        mock_user = self.mock_user
        mock_user.username = "test_user"
        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        response = reject_request(self.db, request)
        self.assertEqual(response, f"{request.type.value} from {mock_user.username} rejected")


if __name__ == '__main__':
    unittest.main()

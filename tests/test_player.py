import unittest
from unittest.mock import MagicMock, ANY
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import uuid4
from src.models.player import Player
from src.models.user import User
from src.models.tournament import TournamentParticipants
from src.schemas.player import CreatePlayerRequest
from src.crud.players import (
    create_player,
    read_player_by_id,
    read_current_user_player_profile,
    read_all_players,
    delete_player,
    update_player_with_user
)


class PlayerCRUD_Should(unittest.TestCase):

    def setUp(self):
        """Set up required objects before each test."""
        self.db_session = MagicMock(spec=Session)
        self.player_data = {
            "id": uuid4(),
            "first_name": "John",
            "last_name": "Doe",
            "country": "USA",
            "team_id": uuid4(),
            "matches_played": 10,
            "wins": 6,
            "losses": 3,
            "draws": 1,
            "user_id": uuid4(),
        }
        self.user_data = {
            "id": uuid4(),
            "username": "playeruser",
            "email": "player@example.com"
        }


    def test_create_player(self):
        request = CreatePlayerRequest(**self.player_data)
        self.db_session.query().filter_by().first.return_value = None

        result = create_player(self.db_session, request)

        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()
        self.db_session.refresh.assert_called_once_with(result)

        assert result.first_name == self.player_data['first_name']
        assert result.last_name == self.player_data['last_name']


    def test_read_player_by_id_success(self):
        player = Player(**self.player_data)
        
        filter_mock = MagicMock()
        self.db_session.query().filter_by.return_value = filter_mock
        filter_mock.first.return_value = player

        result = read_player_by_id(self.db_session, player.id)

        assert result == player
        self.db_session.query().filter_by.assert_called_once_with(id=player.id)
        filter_mock.first.assert_called_once()

    def test_read_player_by_id_not_found(self):
        self.db_session.query().filter_by().first.return_value = None

        with self.assertRaises(HTTPException) as excinfo:
            read_player_by_id(self.db_session, uuid4())

        assert excinfo.exception.status_code == 404
        assert excinfo.exception.detail == "Player not found"


    def test_read_current_user_player_profile_success(self):
        player = Player(**self.player_data)
        user = User(**self.user_data)
        player.user_id = user.id

        query_mock = self.db_session.query.return_value
        query_mock.filter_by.return_value = query_mock
        query_mock.filter_by().first.return_value = player

        result = read_current_user_player_profile(self.db_session, user)

        assert result == player

        query_mock.filter_by.assert_any_call(user_id=user.id)
        query_mock.filter_by().first.assert_called_once()

    def test_read_current_user_player_profile_not_found(self):
        user = User(**self.user_data)
        self.db_session.query().filter_by().first.return_value = None

        with self.assertRaises(HTTPException) as excinfo:
            read_current_user_player_profile(self.db_session, user)

        assert excinfo.exception.status_code == 404
        assert excinfo.exception.detail == "User has no Player profile"


    def test_read_all_players_with_tournament_id(self):
        tournament_id = uuid4()
        player = Player(**self.player_data)

        query_mock = self.db_session.query.return_value
        join_mock = query_mock.join.return_value
        filter_mock = join_mock.filter.return_value
        order_by_mock = filter_mock.order_by.return_value
        order_by_mock.all.return_value = [player]

        result = read_all_players(self.db_session, tournament_id=tournament_id)

        assert result is not None
        assert len(result) == 1
        assert result[0].id == player.id
        assert result[0].first_name == player.first_name
        assert result[0].last_name == player.last_name

        self.db_session.query.assert_called_once_with(Player)
        query_mock.join.assert_called_once_with(TournamentParticipants, ANY)
        join_mock.filter.assert_called_once_with(ANY)
        filter_mock.order_by.assert_called_once_with(Player.first_name)
        order_by_mock.all.assert_called_once()

    def test_delete_player_success(self):
        player = Player(**self.player_data)
        self.db_session.query().filter_by().first.return_value = player
        mock_current_user = User(id=uuid4(), username="testuser", role='ADMIN')

        result = delete_player(self.db_session, player.id,mock_current_user)

        assert result is True
        self.db_session.delete.assert_called_once_with(player)
        self.db_session.commit.assert_called_once()

    def test_delete_player_not_found(self):
        self.db_session.query().filter_by().first.return_value = None
        mock_current_user = User(id=uuid4(), username="testuser", role='ADMIN')

        with self.assertRaises(HTTPException) as excinfo:
            delete_player(self.db_session, uuid4(), mock_current_user)

        assert excinfo.exception.status_code == 404
        assert excinfo.exception.detail == "Player not found"

    def test_update_player_with_user_success(self):
        player = Player(**self.player_data)
        user = User(**self.user_data)

        self.db_session.query().filter_by().first.side_effect = [player, user]

        result = update_player_with_user(self.db_session, player.id, user.id)

        assert result.user_id == user.id
        self.db_session.commit.assert_called_once()
        self.db_session.refresh.assert_called_once_with(player)

    def test_update_player_with_user_player_not_found(self):
        user = User(**self.user_data)
        self.db_session.query().filter_by().first.side_effect = [None, user]

        with self.assertRaises(HTTPException) as excinfo:
            update_player_with_user(self.db_session, uuid4(), user.id)

        assert excinfo.exception.status_code == 404
        assert excinfo.exception.detail == "Player not found"

    def test_update_player_with_user_user_not_found(self):
        player = Player(**self.player_data)
        self.db_session.query().filter_by().first.side_effect = [player, None]

        with self.assertRaises(HTTPException) as excinfo:
            update_player_with_user(self.db_session, player.id, uuid4())

        assert excinfo.exception.status_code == 404
        assert excinfo.exception.detail == "User not found"
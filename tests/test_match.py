import uuid
import unittest
from datetime import datetime, timedelta
from fastapi import HTTPException
from src.models.match import Match
from src.models.player import Player
from src.models.user import User
from src.schemas.match import CreateMatchRequest, MatchResult, MatchUpdateTime
from src.crud.matches import create_match, read_match_by_id, read_all_matches, update_match_score, update_match_date, delete_match, update_player_stats_after_match
from sqlalchemy.orm import Session


class MatchCRUD_Should(unittest.TestCase):

    def setUp(self):
        self.mock_db_session = unittest.mock.MagicMock(spec=Session)
        
        self.match_data = CreateMatchRequest(
            player_a=uuid.uuid4(),
            player_b=uuid.uuid4(),
            start_time=datetime.now() + timedelta(minutes=1),
            end_time=datetime.now() + timedelta(minutes=90),
            tournament_id=None,
            format="score",
            stage=1,
            serial_number=1,
            end_condition=3,
            prize= 1
        )
        
        self.match = Match(
            id=uuid.uuid4(),
            player_a_id=self.match_data.player_a,
            player_b_id=self.match_data.player_b,
            start_time=datetime.now() + timedelta(minutes=1),
            end_time=datetime.now() + timedelta(minutes=90),
            score_a=0,
            score_b=0,
            result_code=None,
            tournament_id=None,
            author_id=None,
            stage=1,
            serial_number=1
        )

    def test_create_match(self):
        self.mock_db_session.query().filter().first.return_value = None
        
        mock_current_user = User(id=uuid.uuid4(), username="testuser")
        match = create_match(self.mock_db_session, self.match_data, mock_current_user)

        self.assertIsNotNone(match)
        self.assertEqual(match.player_a_id, self.match_data.player_a)
        self.assertEqual(match.player_b_id, self.match_data.player_b)

    def test_read_match_by_id(self):
        self.mock_db_session.query().filter().first.return_value = self.match
        result = read_match_by_id(self.mock_db_session, self.match.id)
        self.assertEqual(result.id, self.match.id)
        self.assertEqual(result.player_a_id, self.match.player_a_id)

    def test_read_match_not_found(self):
        self.mock_db_session.query().filter().first.return_value = None
        with self.assertRaises(HTTPException):
            read_match_by_id(self.mock_db_session, uuid.uuid4())

    def test_read_all_matches(self):
        self.mock_db_session.query().all.return_value = [self.match]
        matches = read_all_matches(self.mock_db_session)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].id, self.match.id)

    def test_update_match_score(self):
        updates = MatchResult(score_a=3, score_b=1, result_code="player 1")
        self.mock_db_session.query().filter().first.return_value = self.match
        mock_current_user = User(id=uuid.uuid4(), username="testuser", role='ADMIN')
        updated_match = update_match_score(self.match.id, updates, self.mock_db_session, mock_current_user)
        self.assertEqual(updated_match.score_a, 3)
        self.assertEqual(updated_match.score_b, 1)
        self.assertIsNotNone(updated_match.result_code)

    def test_update_match_score_invalid(self):
        updates = MatchResult(score_a=5, score_b=5, result_code="player 1")
        self.mock_db_session.query().filter().first.return_value = self.match
        mock_current_user = User(id=uuid.uuid4(), username="testuser", role='ADMIN')
        with self.assertRaises(HTTPException):
            update_match_score(self.match.id, updates, self.mock_db_session, mock_current_user)

    def test_update_match_date(self):
        updates = MatchUpdateTime(start_time=datetime.now() + timedelta(days=1), end_time=datetime.now() + timedelta(days=1, minutes=90))
        self.mock_db_session.query().filter().first.return_value = self.match
        mock_current_user = User(id=uuid.uuid4(), username="testuser", role='ADMIN')
        updated_match = update_match_date(self.mock_db_session, self.match.id, updates, mock_current_user)
        self.assertEqual(updated_match.start_time, updates.start_time)
        self.assertEqual(updated_match.end_time, updates.end_time)

    def test_delete_match(self):
        self.mock_db_session.query().filter().first.return_value = self.match
        mock_current_user = User(id=uuid.uuid4(), username="testuser", role='ADMIN')
        success = delete_match(self.mock_db_session, self.match.id, mock_current_user)
        self.assertTrue(success)

    def test_delete_match_not_found(self):
        self.mock_db_session.query().filter().first.return_value = None
        mock_current_user = User(id=uuid.uuid4(), username="testuser", role='ADMIN')
        with self.assertRaises(HTTPException):
            delete_match(self.mock_db_session, uuid.uuid4(), mock_current_user)

    def test_update_player_stats_after_match(self):
        self.mock_db_session.query().filter().first.side_effect = [self.match, Player(id=uuid.uuid4()), Player(id=uuid.uuid4())] 
        mock_current_user = User(id=uuid.uuid4(), username="testuser", role='ADMIN')
        result = update_player_stats_after_match(self.mock_db_session, self.match.id, mock_current_user)
        self.assertEqual(result['detail'], "Player statistics updated successfully")

    def test_update_player_stats_not_found(self):

        self.mock_db_session.query().filter_by().first.side_effect = [None, None, None]
        mock_current_user = User(id=uuid.uuid4(), username="testuser", role='ADMIN')
        with self.assertRaises(HTTPException) as context:
            update_player_stats_after_match(self.mock_db_session, self.match.id, mock_current_user)
        
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Match not found")
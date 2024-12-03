import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.crud import tournaments
from src.models.tournament import Tournament
from src.models.user import User
from src.schemas.tournament import TournamentSchema, CreateTournamentResponse
from src.common.custom_exceptions import NotFound


class TestCreateTournament(unittest.TestCase):
    def setUp(self):
        # Setup method to create common test data and mocks
        self.mock_db_session = MagicMock(spec=Session)
        self.mock_user = MagicMock(spec=User)
        self.mock_user.id = 1

    @patch("src.crud.tournaments.tournament_format_to_id")  
    @patch("src.crud.tournaments.match_format_to_id")  
    def test_create_successful_tournament(self, mock_match_format_to_id, mock_tournament_format_to_id):
        """
        Test successful tournament creation with valid inputs
        """
        # Arrange
        mock_tournament_format_to_id.return_value = 1
        mock_match_format_to_id.return_value = 1

        tournament_data = TournamentSchema(
            name="Test Championship",
            format="league",
            match_format="time",
            start_time=datetime.now() + timedelta(days=30),
            end_time=datetime.now() + timedelta(days=45),
            prize=5000,
            win_points=3,
            draw_points=1
        )
        # Act
        result = tournaments.create(tournament_data, self.mock_user, self.mock_db_session)

        # Assert
        # Verify database interactions
        self.mock_db_session.add.assert_called_once()
        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once()

        # Verify tournament attributes
        self.assertIsInstance(result, Tournament)
        self.assertEqual(result.name, "Test Championship")
        self.assertEqual(result.author_id, self.mock_user.id)
        self.assertEqual(result.format_id, 1)
        self.assertEqual(result.match_format_id, 1)
        self.assertEqual(result.prize, 5000)
    

    @patch("src.crud.tournaments.tournament_format_to_id")
    @patch("src.crud.tournaments.match_format_to_id")
    def test_create_tournament_invalid_format(self, mock_match_format_to_id, mock_tournament_format_to_id):
        """
        Test tournament creation with an invalid tournament format
        """
        # Arrange
        mock_tournament_format_to_id.return_value = None
        mock_match_format_to_id.return_value = 1

        tournament_data = TournamentSchema(
            name="Invalid Format Tournament",
            format="nonexistent_format",
            match_format="time",
            start_time=datetime.now() + timedelta(days=30),
            end_time=datetime.now() + timedelta(days=45),
            prize=5000,
            win_points=3,
            draw_points=1
        )

        # Act & Assert
        with self.assertRaises(NotFound) as context:
            tournaments.create(tournament_data, self.mock_user, self.mock_db_session)
        
        self.assertEqual(context.exception.key, "format")
        self.assertEqual(context.exception.key_value, "nonexistent_format")


    @patch("src.crud.tournaments.tournament_format_to_id")
    @patch("src.crud.tournaments.match_format_to_id")
    def test_create_tournament_invalid_match_format(self, mock_match_format_to_id, mock_tournament_format_to_id):
        """
        Test tournament creation with an invalid match format
        """
        # Arrange
        mock_tournament_format_to_id.return_value = 1
        mock_match_format_to_id.return_value = None

        tournament_data = TournamentSchema(
            name="Invalid Match Format Tournament",
            format="league",
            match_format="nonexistent_match_format",
            start_time=datetime.now() + timedelta(days=30),
            end_time=datetime.now() + timedelta(days=45),
            prize=5000,
            win_points=3,
            draw_points=1
        )

        # Act & Assert
        with self.assertRaises(NotFound) as context:
            tournaments.create(tournament_data, self.mock_user, self.mock_db_session)
        
        self.assertEqual(context.exception.key, "match_format")
        self.assertEqual(context.exception.key_value, "nonexistent_match_format")


if __name__ == '__main__':
    unittest.main()

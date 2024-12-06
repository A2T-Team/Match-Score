import unittest
from unittest.mock import MagicMock, patch, Mock, call
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.crud import tournaments
from src.models.tournament import Tournament, TournamentParticipants
from src.models.player import Player
from src.models.user import User
from src.schemas.tournament import (
    TournamentSchema,
    CreateTournamentResponse,
    Participant,
)
from src.common.custom_exceptions import NotFound
from pydantic import ValidationError
from uuid import uuid4


class TournamentCRUD_Should(unittest.TestCase):
    def setUp(self):
        # Setup method to create common test data and mocks
        self.mock_db_session = MagicMock(spec=Session)
        self.mock_user = MagicMock(spec=User)
        self.mock_user.id = 1

    @patch("src.crud.tournaments.tournament_format_to_id")
    @patch("src.crud.tournaments.match_format_to_id")
    def test_create_successful_tournament(
        self, mock_match_format_to_id, mock_tournament_format_to_id
    ):
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
            draw_points=1,
        )
        # Act
        result = tournaments.create(
            tournament_data, self.mock_user, self.mock_db_session
        )

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

    def test_create_tournament_invalid_format(self):
        """
        Test tournament creation with an invalid tournament format

        This test verifies that:
        1. Pydantic raises a ValidationError for an invalid format
        2. The error message correctly indicates the allowed formats
        """

        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            TournamentSchema(
                name="Invalid Format Tournament",
                format="nonexistent_format",  # Invalid format
                match_format="time",
                start_time=datetime.now() + timedelta(days=30),
                end_time=datetime.now() + timedelta(days=45),
                prize=5000,
                win_points=3,
                draw_points=1,
            )

        # Additional validation of the error
        validation_error = context.exception

        # Check that the error is related to the format field
        self.assertTrue(
            any(
                error["loc"] == ("format",)
                and "Tournament format must be 'league' or 'knockout'" in error["msg"]
                for error in validation_error.errors()
            ),
            "Did not find expected error message for invalid format",
        )

    def test_create_tournament_invalid_match_format(self):
        """
        Test tournament creation with an invalid match format
        """

        with self.assertRaises(ValidationError) as context:
            TournamentSchema(
                name="Invalid Match Format Tournament",
                format="league",
                match_format="nonexistent_match_format",
                start_time=datetime.now() + timedelta(days=30),
                end_time=datetime.now() + timedelta(days=45),
                prize=5000,
                win_points=3,
                draw_points=1,
            )

        # Additional validation of the error
        validation_error = context.exception

        # Check that the error is related to the format field
        self.assertTrue(
            any(
                error["loc"] == ("match_format",)
                and "Match format must be 'time' or 'score'" in error["msg"]
                for error in validation_error.errors()
            ),
            "Did not find expected error message for invalid format",
        )

    def test_get_tournament_existing_tournament(self):
        """
        Test retrieving an existing tournament by its ID.

        This test verifies that:
        1. The function correctly returns a Tournament object when the ID exists
        2. The database query is performed with the correct tournament ID
        """
        # Arrange
        # Create a mock database session
        mock_db_session = Mock(spec=Session)

        # Create a mock tournament with a specific ID
        mock_tournament_id = uuid4()
        mock_tournament = MagicMock()
        mock_tournament.id = mock_tournament_id

        # Configure the mock query to return the mock tournament
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value.first.return_value = mock_tournament

        # Act
        result = tournaments.get_tournament(mock_db_session, mock_tournament_id)

        # Assert
        # Check that the result is the mock tournament
        self.assertEqual(result, mock_tournament)

        # Verify the database query was called correctly
        mock_db_session.query.assert_called_once_with(Tournament)
        mock_query.filter.assert_called_once()
        filter_args = mock_query.filter.call_args[0][0]

        # Compare the right side of the expression (the value)
        # Extract the actual value used in the comparison
        if hasattr(filter_args.right, "value"):
            actual_value = filter_args.right.value
        else:
            actual_value = filter_args.right

        # Compare the UUIDs
        self.assertEqual(str(actual_value), str(mock_tournament_id))

    def test_get_tournament_nonexistent_tournament(self):
        """
        Test retrieving a tournament that does not exist.

        This test verifies that:
        1. The function returns None when no tournament is found
        2. The database query is performed correctly
        """
        # Arrange
        mock_db_session = Mock(spec=Session)
        nonexistent_tournament_id = uuid4()

        # Configure the mock query to return None
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query

        # Act
        result = tournaments.get_tournament(mock_db_session, nonexistent_tournament_id)

        # Assert
        # Check that the result is None
        self.assertIsNone(result)

        # Verify the database query was called correctly
        mock_db_session.query.assert_called_once_with(Tournament)
        mock_query.filter.assert_called_once()
        mock_query.filter().first.assert_called_once()

    def test_view_all_tournaments(self):
        """Test retrieving tournaments with default parameters"""
        # Arrange
        mock_db_session = Mock(spec=Session)
        mock_tournaments = [MagicMock(), MagicMock()]

        # Configure mock query
        mock_query = mock_db_session.query.return_value
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_tournaments

        # Act
        result = tournaments.view_all_tournaments(mock_db_session)

        # Assert
        mock_db_session.query.assert_called_once_with(Tournament)
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(10)
        self.assertEqual(result, mock_tournaments)

    def test_view_all_tournaments_with_search(self):
        """Test retrieving tournaments with search parameter"""
        # Arrange
        mock_db_session = Mock(spec=Session)
        mock_tournaments = [MagicMock()]
        search_term = "Summer"

        # Configure mock query
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value.offset.return_value.limit.return_value.all.return_value = (
            mock_tournaments
        )

        # Act
        result = tournaments.view_all_tournaments(mock_db_session, search=search_term)

        # Assert
        mock_query.filter.assert_called_once()
        filter_args = mock_query.filter.call_args[0][0]

        # Detailed debugging and assertions
        filter_str = str(filter_args)

        # Check for case-insensitive matching
        self.assertTrue(
            "lower(" in filter_str.lower(), "Query should use case-insensitive matching"
        )

        # Check that it's using LIKE
        self.assertTrue(
            "like" in filter_str.lower(), "Query should use LIKE for partial matching"
        )

        self.assertTrue(
            "tournaments.name" in filter_str,
            "Filter should be applied on the name column",
        )

        self.assertEqual(result, mock_tournaments)

    def test_view_all_tournaments_sorted_desc(self):
        """Test retrieving tournaments sorted in descending order"""
        # Arrange
        mock_db_session = Mock(spec=Session)
        mock_tournaments = [MagicMock(), MagicMock()]

        # Configure mock query
        mock_query = mock_db_session.query.return_value
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
            mock_tournaments
        )

        # Act
        result = tournaments.view_all_tournaments(mock_db_session, sort="desc")

        # Assert
        mock_query.order_by.assert_called_once()

        order_by_args = mock_query.order_by.call_args[0][0]
        # Check if it's descending order on start_time
        self.assertTrue(
            str(order_by_args).endswith("DESC"),
            f"Expected descending order, got: {order_by_args}",
        )

        # Verify the column being sorted
        self.assertTrue(
            "start_time" in str(order_by_args), "Should sort by start_time column"
        )

        self.assertEqual(result, mock_tournaments)

    def test_view_all_tournaments_sorted_asc(self):
        """Test retrieving tournaments sorted in ascending order"""
        # Arrange
        mock_db_session = Mock(spec=Session)
        mock_tournaments = [MagicMock(), MagicMock()]

        # Configure mock query
        mock_query = mock_db_session.query.return_value
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
            mock_tournaments
        )

        # Act
        result = tournaments.view_all_tournaments(mock_db_session, sort="asc")

        # Assert
        mock_query.order_by.assert_called_once()

        order_by_args = mock_query.order_by.call_args[0][0]
        # Check if it's asc order on start_time
        self.assertTrue(
            str(order_by_args).endswith("ASC"),
            f"Expected asc order, got: {order_by_args}",
        )

        # Verify the column being sorted
        self.assertTrue(
            "start_time" in str(order_by_args), "Should sort by start_time column"
        )

        self.assertEqual(result, mock_tournaments)

    def test_view_all_tournaments_with_pagination(self):
        """Test retrieving tournaments with custom offset and limit"""
        # Arrange
        mock_db_session = Mock(spec=Session)
        mock_tournaments = [MagicMock(), MagicMock()]

        # Configure mock query
        mock_query = mock_db_session.query.return_value

        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_tournaments

        # Act
        result = tournaments.view_all_tournaments(mock_db_session, offset=20, limit=5)

        # Assert
        mock_db_session.query.assert_called_once_with(Tournament)
        mock_query.offset.assert_called_once_with(20)
        mock_query.limit.assert_called_once_with(5)
        mock_query.all.assert_called_once()

        self.assertEqual(result, mock_tournaments)

    def test_get_participant_case_insensitive(self):
        """
        Test that the function works with case-insensitive searches.
        """
        # Arrange
        mock_db_session = Mock(spec=Session)

        test_player = MagicMock()
        test_player.first_name = "Jane"
        test_player.last_name = "Smith"

        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value.first.return_value = test_player

        # Search with different casing
        search_participant = Participant(first_name="jAnE", last_name="sMiTh")

        # Act
        result = tournaments.get_participant(mock_db_session, search_participant)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result, test_player)
        self.assertEqual(result.first_name, "Jane")
        self.assertEqual(result.last_name, "Smith")

        mock_db_session.query.assert_called_once_with(Player)
        mock_query.filter.assert_called_once()

        filter_args = mock_query.filter.call_args[0][0]
        filter_str = str(filter_args)

        self.assertTrue(
            "like" in filter_str.lower(), "Query should use LIKE for partial matching"
        )
        self.assertTrue(
            "players.first_name" in filter_str,
            "Filter should be applied on the first_name column",
        )
        self.assertTrue(
            "players.last_name" in filter_str,
            "Filter should be applied on the last_name column",
        )

    def test_get_participant_not_found(self):
        """
        Test that the function returns None when no participant matches the search criteria.
        """
        # Arrange
        mock_db_session = Mock(spec=Session)

        # Mock query chain to simulate no matching player found
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value.first.return_value = None  # No result

        # Search participant with case-insensitive mismatched details
        search_participant = Participant(first_name="Nonexistent", last_name="Player")

        # Act
        result = tournaments.get_participant(mock_db_session, search_participant)

        # Assert
        self.assertIsNone(result)  # Verify that the result is None

        # Ensure the query and filter were executed
        mock_db_session.query.assert_called_once_with(Player)
        mock_query.filter.assert_called_once()

    
    def test_create_player_success(self):
        """
        Test that a new player is created and added to the database successfully.
        """
        # Arrange
        mock_db_session = Mock(spec=Session)
        
        # Input data
        participant = Participant(first_name="John", last_name="Doe")
        
        # Mock Player object to simulate the result of the database operation
        mock_player = MagicMock(spec=Player)
        mock_player.first_name = "John"
        mock_player.last_name = "Doe"

        # Act
        result = tournaments.create_player(mock_db_session, participant)
        
        # Assert
        self.assertIsInstance(result, Player)
        self.assertIsNotNone(result)
        self.assertEqual(result.first_name, "John")
        self.assertEqual(result.last_name, "Doe")
        
        # Ensure that the correct database methods were called
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(result) 
    

    def test_participant_not_found(self):
        """
        Test scenario where the participant does not exist in the database.
        """
        # Arrange
        mock_db_session = Mock(spec=Session)
        mock_tournament_id = uuid4()
        participant = Participant(first_name="John", last_name="Doe")

        # Mock get_participant to return None
        with patch('src.crud.tournaments.get_participant', return_value=None) as mock_get_participant:
            result = tournaments.get_tournament_participant(
                mock_db_session, 
                participant, 
                mock_tournament_id
            )
            # Assert that get_participant was called with correct arguments
            mock_get_participant.assert_called_once_with(
                mock_db_session, 
                participant
            )
            # Verify that the result is None
            self.assertIsNone(result)
    

    def test_participant_not_in_tournament(self):
        """
        Test scenario where the participant exists but is not registered 
        for the specified tournament.
        """
        # Arrange
        mock_db_session = Mock(spec=Session)
        mock_tournament_id = uuid4()
        participant = Participant(first_name="John", last_name="Doe")

        # Create a mock database player
        mock_db_player = Player(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
    )
        
        with patch('src.crud.tournaments.get_participant', return_value=mock_db_player) as mock_get_participant:
            # Configure the session query to return None
            mock_query = Mock()
            mock_db_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = None
        
            result = tournaments.get_tournament_participant(
                mock_db_session,
                participant,
                mock_tournament_id
            )
            
            # Verify get_participant was called
            mock_get_participant.assert_called_once_with(
                mock_db_session,
                participant
            )
        
            # Verify the query was constructed correctly
            mock_db_session.query.assert_called_once_with(TournamentParticipants)
        
            # Verify filter was called with correct conditions
            mock_query.filter.assert_called_once()
            # Get the actual filter arguments
            filter_call_args = mock_query.filter.call_args[0][0]
            
            self.assertIsNotNone(filter_call_args, "Filter arguments should not be None")
            
            # Check if the filter includes the correct conditions
            conditions = str(filter_call_args)
            self.assertIn("tournament_participants.player_id", conditions, "Player ID should be in filter conditions")
            self.assertIn("tournament_participants.tournament_id", conditions, "Tournament ID should be in filter conditions")
            
            # Verify first() was called
            mock_query.first.assert_called_once()
            
            # Verify the result is None
            self.assertIsNone(result)


    def test_participant_in_tournament(self):
        """
        Test scenario where the participant is registered in the tournament.
        """
        # Arrange
        mock_db_session = Mock(spec=Session)
        mock_tournament_id = uuid4()
        participant = Participant(first_name="John", last_name="Doe")

        # Create a mock database player
        mock_db_player = Player(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
    )
        
        with patch('src.crud.tournaments.get_participant', return_value=mock_db_player) as mock_get_participant:
            # Configure the session query to return None
            mock_query = Mock()
            mock_db_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = mock_db_player
        
            result = tournaments.get_tournament_participant(
                mock_db_session,
                participant,
                mock_tournament_id
            )
            
            # Verify get_participant was called
            mock_get_participant.assert_called_once_with(
                mock_db_session,
                participant
            )
        
            # Verify the query was constructed correctly
            mock_db_session.query.assert_called_once_with(TournamentParticipants)
        
            # Verify filter was called with correct conditions
            mock_query.filter.assert_called_once()
            # Get the actual filter arguments
            filter_call_args = mock_query.filter.call_args[0][0]
            
            self.assertIsNotNone(filter_call_args, "Filter arguments should not be None")
            
            # Check if the filter includes the correct conditions
            conditions = str(filter_call_args)
            self.assertIn("tournament_participants.player_id", conditions, "Player ID should be in filter conditions")
            self.assertIn("tournament_participants.tournament_id", conditions, "Tournament ID should be in filter conditions")
            
            # Verify first() was called
            mock_query.first.assert_called_once()
            
            # Verify the result is None
            self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()

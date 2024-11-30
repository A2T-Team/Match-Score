class NotFound(Exception):
    """Custom exception for resource not found errors."""

    def __init__(self, key: str, key_value: str):
        self.key = key
        self.key_value = key_value
        super().__init__(f"{key} '{key_value}' not found.")


class InvalidNumberOfPlayers(Exception):
    """Custom exception for errors with count of players."""

    def __init__(self, number_of_players: int, tournament_format: str):
        self.number_of_players = number_of_players
        if tournament_format == "knockout":
            super().__init__(
                f"Knockout tournament has {number_of_players} player(s). "
                "The number of players must be a power of two."
            )
        else:
            super().__init__(
                f"League tournament has {number_of_players} player(s). "
                "The number of players must be at least 3"
            )


class InvalidRequest(Exception):
    """Custom exception for invalid request"""

    def __init__(self, error_messag: str):
        super().__init__(error_messag)

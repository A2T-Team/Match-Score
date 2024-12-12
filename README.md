
# Match-Score API - A2T Team
![A2T Logo](https://github.com/user-attachments/assets/29f76560-80b3-4bd5-81c1-447e86b41da3)

# Match-Score API

The **Match-Score** API is a Tracker API built with FastAPI that allows users to create tournaments, matches, and players, track scoring, and maintain player statistics. It provides endpoints for user authentication, tournament management, player statistics, and more.


## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
  - [Player Management](#player-management)
  - [Tournament Management](#tournament-management)
  - [Match Management](#match-management)
  - [Request Management](#request-management)
  - [Authentication](#authentication)
- [Running Tests](#running-tests)
- [License](#license)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/A2T-Team/Match-Score.git
cd match-score
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

Create a `.env` file in the root directory of the project and add the following environment variables:

```env
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
```

5. Database Setup - Scripts available in the folder `scripts` for initializing and populating the database.

## Usage

1. Start the FastAPI server:

```bash
uvicorn main:app --reload
```

2. The API will be available at `http://127.0.0.1:8000`.

## Running Tests

1. Install the test dependencies:

```bash
pip install -r requirements-test.txt
```

2. Run the tests:

```bash
pytest
```

## API Endpoints

### Player Management

- **Get All Players**
  - **URL:** `/api/v1/players/`
  - **Method:** `GET`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Retrieves a list of all players.
  - **Response:**
    - `200 OK`: List of `PlayerResponse` objects.

- **Create Player**
  - **URL:** `/api/v1/players/`
  - **Method:** `POST`
  - **Body:**
    ```json
    {
      "first_name": "John",
      "last_name": "Doe",
      "country": "USA"
    }
    ```
  - **Description:** Registers a new player with the provided details. Only accessible by `ADMIN` or `DIRECTOR`.
  - **Response:**
    - `201 Created`: The created `PlayerResponse` object.

- **Get Player by ID**
  - **URL:** `/api/v1/players/{player_id}`
  - **Method:** `GET`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Retrieves a player by their ID.
  - **Response:**
    - `200 OK`: The `PlayerResponse` object.

- **Update Player**
  - **URL:** `/api/v1/players/{player_id}`
  - **Method:** `PUT`
  - **Body:**
    ```json
    {
      "first_name": "Jane",
      "last_name": "Doe",
      "country": "USA"
    }
    ```
  - **Description:** Updates an existing player's information. Only accessible by `ADMIN` or `DIRECTOR`.
  - **Response:**
    - `200 OK`: The updated `PlayerResponse` object.
  
- **Get User Player Profile**
  - **URL:** `/api/v1/players/my_profile`
  - **Method:** `GET`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Retrieves users player profile.
  - **Response:**
    - `200 OK`: The `PlayerResponse` object.

- **Delete Player**
  - **URL:** `/api/v1/players/{player_id}`
  - **Method:** `DELETE`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Deletes player profile.
  - **Response:**
    - `200 OK`  

- **Get Player in Tournament**
  - **URL:** `/api/v1/players/{player_id}/{tournament_id}`
  - **Method:** `GET`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Retrieves players in a tournament.
  - **Response:**
    - `200 OK`: The `ParticipantResponse` object.

### Tournament Management

- **View All Tournaments**
  - **URL:** `/api/v1/tournaments/`
  - **Method:** `GET`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Retrieves a list of all tournaments.
  - **Response:**
    - `200 OK`: List of `TournamentResponse` objects.

- **Create Tournament**
  - **URL:** `/api/v1/tournaments/`
  - **Method:** `POST`
  - **Body:**
    ```json
  {
  "name": "Black Doll Winter 2024",
  "format": "Format must be 'league' or 'knockout'",
  "match_format": "Format must be 'time' or 'score'",
  "start_time": "Format must be 'YYYY/MM/DD HH:MM",
  "end_time": "Format must be 'YYYY/MM/DD HH:MM'",
  "prize": 0,
  "win_points": 0,
  "draw_points": 0
  }
    ```
  - **Description:** Creates a new tournament. Only accessible by `ADMIN` or `DIRECTOR`.
  - **Response:**
    - `201 Created`: The created `CreateTournamentResponse` object.

- **View Tournament by ID**
  - **URL:** `/api/v1/tournaments/{tournament_id}`
  - **Method:** `GET`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Retrieves a tournament by its ID.
  - **Response:**
    - `200 OK`: The `Tournament` object.

- **Update Tournament**
  - **URL:** `/api/v1/tournaments/{tournament_id}`
  - **Method:** `PATCH`
  - **Body:**
    ```json
  {
  "name": "Black Doll Winter 2024",
  "start_time": "Format must be 'YYYY/MM/DD HH:MM",
  "end_time": "Format must be 'YYYY/MM/DD HH:MM",
  "prize": 0
}
    ```
  - **Description:** Updates a tournament. Only accessible by `ADMIN` or `DIRECTOR`.
  - **Response:**
    - `201 Created`: Update `UpdateTournamentResponse` object.

- **Delete Tournament**
  - **URL:** `/api/v1/tournaments/{tournament_id}`
  - **Method:** `DELETE`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Deletes tournament.
  - **Response:**
    - `200 OK`  

- **Add Players**
  - **URL:** `/api/v1/tournaments/{tournament_id}/players`
  - **Method:** `PUT`
  - **Body:**
    ```json
  [
    {
      "first_name": "Example",
      "last_name": "Example"
    }
  ]
    ```
  - **Description:** Adds a list of players to tournament. Only accessible by `ADMIN` or `DIRECTOR`.
  - **Response:**
    - `201 Created`: The list of `Participant` objects.

- **Delete Players**
  - **URL:** `/api/v1/tournaments/{tournament_id}/players`
  - **Method:** `DELETE`
  - **Body:**
    ```json
  [
    {
      "first_name": "Example",
      "last_name": "Example"
    }
  ]
    ```
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Deletes list of players from the tournament.
  - **Response:**
    - `200 OK`

- **Create Matches**
  - **URL:** `/api/v1/tournaments/{tournament_id}/matches`
  - **Method:** `PUT`
  - **Description:** Creates the matches of the tournament. Only accessible by `ADMIN` or `DIRECTOR`.
  - **Response:**
    - `201 Created`

- **Update Match**
  - **URL:** `/api/v1/tournaments/{tournament_id}/matches/{match_id}`
  - **Method:** `PUT`
  - **Body:**
    ```json
  [
  "string"
  ]
    ```
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Updates a match from the tournament.
  - **Response:**
    - `200 OK`

### Match Management

- **Get All Matches**
  - **URL:** `/api/v1/matches/`
  - **Method:** `GET`
  - **Description:** Retrieves a list of all matches.
  - **Response:**
    - `200 OK`: List of `MatchResponse` objects.

- **Create Match**
  - **URL:** `/api/v1/matches/`
  - **Method:** `POST`
  - **Body:**
    ```json
    {
      "format": "Format must be 'time' or 'score'",
      "end_condition": 0,
      "player_a": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "player_b": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "start_time": "Format must be 'YYYY/MM/DD HH:MM'",
      "end_time": "Format must be 'YYYY/MM/DD HH:MM'",
      "prize": 0,
      "tournament_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "stage": 0,
      "serial_number": 0
    }
    ```
  - **Description:** Creates a new match between two players. Only accessible by `ADMIN` or `DIRECTOR`.
  - **Response:**
    - `201 Created`: The created `MatchResponse` object.

- **Get Match by ID**
  - **URL:** `/api/v1/matches/{match_id}`
  - **Method:** `GET`
  - **Description:** Retrieves a match by its ID.
  - **Response:**
    - `200 OK`: The `MatchResponse` object.

- **Update Match Score**
  - **URL:** `/api/v1/matches/{match_id}/score`
  - **Method:** `PATCH`
  - **Body:**
    ```json
    {
      "score_a": 0,
      "score_b": 0,
      "result_code": "string"
    }
    ```
  - **Description:** Updates the score of a match. Only accessible by `ADMIN` or `DIRECTOR`.
  - **Response:**
    - `200 OK`: The `MatchResponse` object.

- **Update Match Date**
  - **URL:** `/api/v1/matches/{match_id}/date`
  - **Method:** `PATCH`
  - **Body:**
    ```json
    {
      "start_time": "Format must be 'YYYY/MM/DD HH:MM'",
      "end_time": "Format must be 'YYYY/MM/DD HH:MM'"
    }
    ```
  - **Description:** Updates the date of a match. Only accessible by `ADMIN` or `DIRECTOR`.
  - **Response:**
    - `200 OK`: The `MatchResponse` object.

- **Delete Match**
  - **URL:** `/api/v1/matches/{match_id}`
  - **Method:** `DELETE`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Deletes match.
  - **Response:**
    - `200 OK`

- **Update Player Stats**
  - **URL:** `/api/v1/matches/match/{match_id}/update_stats`
  - **Method:** `PUT`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Updates the player stats after the match.
  - **Response:**
    - `200 OK`


### Request Management

- **View Requests**
  - **URL:** `/api/v1/requests/`
  - **Method:** `GET`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Retrieves a list of all requests. Admin can filter with search by `request status`. Only accessible by `ADMIN`.
  - **Response:**
    - `200 OK`: List of `Request` objects.

- **Create Request**
  - **URL:** `/api/v1/requests/`
  - **Method:** `POST`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Body:**
    ```json
    {
      "request_type": "Promote Request",
      "request_reason": "If you want to link your account to a player, write only the player's firstname and lastname here."
    }
    ```
  - **Description:** Creates a new request. Only accessible by `USER` or `DIRECTOR`.
  - **Response:**
    - `201 Created`: The created `Request` object.

- **Open Request By ID**
  - **URL:** `/api/v1/requests/{request_id}`
  - **Method:** `GET`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Retrieves a request by its ID. Admin can choose to accept or reject the request. Only accessible by `ADMIN`.
  - **Response:**
    - `200 OK`: The `Request` object.

### Authentication

- **Register**
  - **URL:** `/api/v1/users/register`
  - **Method:** `POST`
  - **Body:**
    ```json
    {
      "username": "johndoe",
      "email": "johndoe@gmail.com",
      "password": "password"
    }
    ```
  - **Description:** Register a new user.
  - **Response:**
    - `200 OK`

- **Login**
  - **URL:** `/api/v1/users/login`
  - **Method:** `POST`
  - **Body:**
    ```json
    {
    "username": "johndoe",
    "password": "password"
    }
    ```
  - **Description:** Authenticates a user and returns a JWT token.
  - **Response:**
    - `200 OK`: A dictionary containing the JWT token.

- **Logout**
  - **URL:** `/logout`
  - **Method:** `POST`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Logs out the user by invalidating the JWT token.
  - **Response:**
    - `200 OK`: A message indicating the user has been logged out.

- **View All Users**
  - **URL:** `/api/v1/users/`
  - **Method:** `GET`
  - **Description:** Retrives all users. Can search by `username` or `email`. can set a limit.
  - **Response:**
    - `200 OK`: List of `User` objects.

- **View Current User**
- **URL:** `/api/v1/users/me`
- **Method:** `GET`
- **Description:** Retrieves the current user's information.
- **Response:**
  - `200 OK`: The `User` object.

- **Update Current User Email**
- **URL:** `/api/v1/users/me/email`
- **Method:** `PUT`
- **Body:**
  ```json
  {
    "email": "johndoe@gmail.com"
    }
    ```
- **Description:** Updates the current user's email.
- **Response:**
  - `200 OK`: The updated `User` object.

- **Update User Credentials**
  - **URL:** `/api/v1/users/`
  - **Method:** `PUT`
  - **Description:** Updates users credentials. Search by username. Only accessible by `ADMIN`.
  - **Body:**
    ```json
    {
    "email": "johmdoe@gmail.com",
    "role": "user"
    }
    ```
  - **Response:**
    - `200 OK`

- **Delete User by Username**
  - **URL:** `/api/v1/users/{username}/delete`
  - **Method:** `DELETE`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Deletes user by username. Only accessible by `ADMIN`.
  - **Response:**
    - `200 OK`

## License

This project is licensed under the MIT License. See the LICENSE file for details.

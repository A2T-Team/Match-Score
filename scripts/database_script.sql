INSERT INTO tournaments.tournament_format (id, type) 
VALUES 
    (1, 'league'), 
    (2, 'knockout');

INSERT INTO tournaments.match_format (id, type) 
VALUES 
    (1, 'score'), 
    (2, 'time');

INSERT INTO tournaments.result_codes (id, result) 
VALUES 
    (1, 'player 1'),
    (2, 'player 2'), 
    (3, 'draw');
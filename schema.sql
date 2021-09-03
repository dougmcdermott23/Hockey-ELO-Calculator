CREATE TABLE IF NOT EXISTS game (
    game_id BIGSERIAL NOT NULL PRIMARY KEY,
    season_id INT NOT NULL,
    game_type INT NOT NULL,
    game_number INT NOT NULL,
    game_date DATE NOT NULL,
    start_time TIMESTAMP,
    venue VARCHAR(150),
    home_team VARCHAR(50) NOT NULL,
    away_team VARCHAR(50) NOT NULL,
    home_score INT NOT NULL,
    away_score INT NOT NULL,
    game_status VARCHAR(50) NOT NULL,
    home_rating_start FLOAT,
    home_rating_end FLOAT,
    away_rating_start FLOAT,
    away_rating_end FLOAT
);
ALTER TABLE game ADD CONSTRAINT unique_game UNIQUE (season_id, game_type, game_number);

CREATE TABLE IF NOT EXISTS team (
    team_id BIGSERIAL NOT NULL PRIMARY KEY,
    team_name VARCHAR(50) NOT NULL,
    team_name_abbreviation VARCHAR(50) NOT NULL,
    current_rating FLOAT NOT NULL
);
ALTER TABLE team ADD CONSTRAINT unique_team_name UNIQUE (team_name);
ALTER TABLE team ADD CONSTRAINT unique_team_name_abbreviation UNIQUE (team_name_abbreviation);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Anaheim Ducks', 'ANA', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Arizona Coyotes', 'ARI', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Boston Bruins', 'BOS', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Buffalo Sabres', 'BUF', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Calgary Flames', 'CGY', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Carolina Hurricanes', 'CAR', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Chicago Blackhawks', 'CHI', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Colorado Avalanche', 'COL', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Columbus Blue Jackets', 'CBJ', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Dallas Stars', 'DAL', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Detroit Red Wings', 'DET', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Edmonton Oilers', 'EDM', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Florida Panthers', 'FLA', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Los Angeles Kings', 'L.A', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Minnesota Wild', 'MIN', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Montreal Canadiens', 'MTL', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Nashville Predators', 'NSH', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('New Jersey Devils', 'N.J', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('New York Islanders', 'NYI', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('New York Rangers', 'NYR', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Ottawa Senators', 'OTT', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Philadelphia Flyers', 'PHI', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Pittsburgh Penguins', 'PIT', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('San Jose Sharks', 'S.J', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Seattle Kraken', 'SEA', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('St. Louis Blues', 'STL', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Tampa Bay Lightning', 'T.B', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Toronto Maple Leafs', 'TOR', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Vancouver Canucks', 'VAN', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Vegas Golden Knights', 'VGK', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Washington Capitals', 'WSH', 0);
INSERT INTO team (team_name, team_name_abbreviation, current_rating) VALUES ('Winnipeg Jets', 'WPG', 0);
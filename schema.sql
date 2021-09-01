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

CREATE TABLE IF NOT EXISTS team (
    team_id BIGSERIAL NOT NULL PRIMARY KEY,
    team_name VARCHAR(50) NOT NULL,
    team_name_abbreviation VARCHAR(50) NOT NULL,
    current_rating FLOAT
);
ALTER TABLE team ADD CONSTRAINT unique_team_name UNIQUE (team_name);
ALTER TABLE team ADD CONSTRAINT unique_team_name_abbreviation UNIQUE (team_name_abbreviation);
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Anaheim Ducks', 'ANA');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Arizona Coyotes', 'ARI');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Boston Bruins', 'BOS');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Buffalo Sabres', 'BUF');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Calgary Flames', 'CGY');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Carolina Hurricanes', 'CAR');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Chicago Blackhawks', 'CHI');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Colorado Avalanche', 'COL');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Columbus Blue Jackets', 'CBJ');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Dallas Stars', 'DAL');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Detroit Red Wings', 'DET');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Edmonton Oilers', 'EDM');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Florida Panthers', 'FLA');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Los Angeles Kings', 'L.A');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Minnesota Wild', 'MIN');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Montreal Canadiens', 'MTL');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Nashville Predators', 'NSH');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('New Jersey Devils', 'N.J');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('New York Islanders', 'NYI');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('New York Rangers', 'NYR');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Ottawa Senators', 'OTT');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Philadelphia Flyers', 'PHI');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Pittsburgh Penguins', 'PIT');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('San Jose Sharks', 'S.J');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Seattle Kraken', 'SEA');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('St. Louis Blues', 'STL');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Tampa Bay Lightning', 'T.B');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Toronto Maple Leafs', 'TOR');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Vancouver Canucks', 'VAN');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Vegas Golden Knights', 'VGK');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Washington Capitals', 'WSH');
INSERT INTO team (team_name, team_name_abbreviation) VALUES ('Winnipeg Jets', 'WPG');
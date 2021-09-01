import math

class Game:
    game_id = None
    season_id = None
    game_type = None
    game_number = None
    date = None
    start_time = None
    venue = None
    home_team = None
    away_team = None
    home_score = None
    away_score = None
    status = None
    home_start_rating = None
    home_end_rating = None
    away_start_rating = None
    away_end_rating = None

    def __init__(self, game_id, date, start_time, venue, home_team, away_team, home_score, away_score, status):
        self.game_id = game_id
        self.date = date
        self.start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
        self.venue = venue
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = int(home_score)
        self.away_score = int(away_score)
        self.status = status

        self.ValidateTeamName()
        self.ParseGameId()

        return

    def ValidateTeamName(self):
        if self.home_team == 'PHX':
            self.home_team = 'ARI'

        if self.away_team == 'PHX':
            self.away_team = 'ARI'

        if self.home_team == 'ATL':
            self.home_team = 'WPG'

        if self.away_team == 'ATL':
            self.away_team = 'WPG'

        return

    def ParseGameId(self):
        game_str = str(self.game_id)
        self.season_id = int(game_str[0:4])
        self.game_type = int(game_str[4:6])
        self.game_number = int(game_str[6:])

    def AreTeamsValid(self, valid_teams):
        return (self.home_team in valid_teams and self.away_team in valid_teams)

    def GetGameInformation(self):
        game_information = [
            self.season_id,
            self.game_type,
            self.game_number,
            self.date,
            self.start_time,
            self.venue,
            self.home_team,
            self.away_team,
            self.home_score,
            self.away_score,
            self.status,
            self.home_start_rating,
            self.home_end_rating,
            self.away_start_rating,
            self.away_end_rating,
        ]

        return game_information

    def CalculateELO(self, home_start_rating, away_start_rating):
        K = 20
        R_home = home_start_rating
        R_away = away_start_rating
        S_home = 0
        S_away = 0

        if self.home_score > self.away_score:
            S_home = 1

        S_away = 1 - S_home

        # Expected Score
        Q_home = math.pow(10, R_home/400)
        Q_away = math.pow(10, R_away/400)
        E_home = Q_home / (Q_home + Q_away)
        E_away = Q_away / (Q_home + Q_away)

        # Updated Rating
        R_home_new = R_home + K * (S_home - E_home)
        R_away_new = R_away + K * (S_away - E_away)

        self.home_start_rating = home_start_rating
        self.home_end_rating = R_home_new
        self.away_start_rating = away_start_rating
        self.away_end_rating = R_away_new

        return
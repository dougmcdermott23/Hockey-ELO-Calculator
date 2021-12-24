import math

class Game:
    game_id: str
    season_id: int
    game_type: int
    game_number: int
    date: str
    start_time: str
    venue: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    status: str
    home_start_rating: float
    home_end_rating: float
    away_start_rating: float
    away_end_rating: float

    def __init__(self,
                 game_id: int,
                 date: str,
                 start_time: str,
                 venue: str,
                 home_team: str,
                 away_team: str,
                 home_score: int,
                 away_score: int,
                 status: str) -> None:
        self.game_id = game_id
        self.date = date
        self.start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        self.venue = venue
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = home_score
        self.away_score = away_score
        self.status = status

        self.validate_team_name()
        self.parse_game_id()

    # Adjust team abbreviations for franchise changes
    def validate_team_name(self) -> None:
        if self.home_team == "PHX":
            self.home_team = "ARI"

        if self.away_team == "PHX":
            self.away_team = "ARI"

        if self.home_team == "ATL":
            self.home_team = "WPG"

        if self.away_team == "ATL":
            self.away_team = "WPG"

    # Game ID is in format YYYYTTNNNNNN (Y - Season, T - Game Type, N - Game Number)
    def parse_game_id(self) -> None:
        game_str = str(self.game_id)
        self.season_id = int(game_str[0:4])
        self.game_type = int(game_str[4:6])
        self.game_number = int(game_str[6:])

    def get_game_information(self) -> list:
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

    def calculate_elo(self, home_start_rating: float, away_start_rating: float, K: float=20) -> None:
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
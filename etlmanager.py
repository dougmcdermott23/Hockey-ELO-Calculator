import hockey_scraper
from pandas.core.frame import DataFrame

import dbutils as db
from constants import GameType
from game import Game

valid_game_types = [GameType.SEASON_GAME_TYPE]

class ETLManager:
    team_ratings: dict

    def __init__(self, team_ratings: dict=None) -> None:
        if team_ratings is None:
            team_ratings = db.get_team_ratings()
        self.team_ratings = team_ratings

    def extract_transform_load(self, start_date: str, end_date: str, retries_limit: int=10) -> bool:
        success = False
        
        try:
            raw_game_data = self.extract_game_data(start_date, end_date, retries_limit)
            if raw_game_data is not None:
                transformed_game_data = self.transform_game_data(raw_game_data)
                success = self.load_game_data(transformed_game_data)
        except Exception as error:
            print(f"Exception in extract_transform_load... {error}")
            raise Exception(error)

        return success

    # Extract game data within date range
    def extract_game_data(self, start_date: str, end_date: str, retries_limit: int=10) -> DataFrame:
        retrieved = False
        retries = 0

        raw_game_data = None
        while retrieved is False and retries < retries_limit:
            try:
                raw_game_data = hockey_scraper.scrape_schedule(start_date, end_date)
                retrieved = True
            except Exception as error:
                retries += 1
                print(f"Exception while retrieving data, trying again... {error}")

        return raw_game_data

    # Takes raw game data, transforms the information with updated team ratings and stores in a list
    def transform_game_data(self, raw_game_data: DataFrame) -> list:
        transformed_game_data = []
        
        for index in range(len(raw_game_data)):
            game = Game(raw_game_data['game_id'][index],
                        raw_game_data['date'][index],
                        raw_game_data['start_time'][index],
                        raw_game_data['venue'][index],
                        raw_game_data['home_team'][index],
                        raw_game_data['away_team'][index],
                        int(raw_game_data['home_score'][index]),
                        int(raw_game_data['away_score'][index]),
                        raw_game_data['status'][index])

            game_data = self.initialize_game_data(game)
            if game_data != None:
                transformed_game_data.append(game_data)
        
        return transformed_game_data

    # Update team ratings and insert transformed game data
    def load_game_data(self, game_data: list) -> bool:
        print(f"[ETLManager] Loading {len(game_data)} games")
        success = db.update_team_ratings(self.team_ratings)
        success &= db.insert_game_data(game_data)
        return success

    def initialize_game_data(self, game: Game) -> list:
        if self.is_game_valid(game):
            game.calculate_elo(self.team_ratings[game.home_team], self.team_ratings[game.away_team])
            self.team_ratings[game.home_team], self.team_ratings[game.away_team] = game.home_end_rating, game.away_end_rating
            return game.get_game_information()
    
    def is_game_valid(self, game: Game) -> bool:
        return self.is_game_type_valid(game) and self.are_teams_valid(game)

    def is_game_type_valid(self, game: Game) -> bool:
        return GameType(game.game_type) in valid_game_types

    def are_teams_valid(self, game: Game) -> bool:
        return (game.home_team in self.team_ratings and game.away_team in self.team_ratings)
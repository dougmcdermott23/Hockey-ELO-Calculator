import hockey_scraper
from pandas.core.frame import DataFrame

from .enums import GameType
from .classes.game import Game
from .dbutils import (get_team_ratings, update_team_ratings, insert_game_data)
from .logging.logger import LogManager

valid_game_types = [GameType.SEASON_GAME_TYPE]

def extract_transform_load(start_date: str,
                           end_date: str,
                           team_ratings: dict = None,
                           retries_limit: int = 10) -> int:
    """ETL pipeline for updating the database. Extract raw game data using the hockey_scraper
    package. Transform the data: validate, calculate the new team ratings, and prepare for loading.
    Load the new team ratings and game information into the database.

    start_date: string for the start date for data extraction
    end_date: string for the end date for data extraction
    team_ratings: dict where the key is the team name and the value is the team rating
    retries_limit: Number of retries to extract game data using the hockey_scraper package

    return: bool saying if the entire process was a success
    """            
    try:
        if team_ratings is None:
            team_ratings = get_team_ratings()

        raw_game_data = extract_game_data(start_date, end_date, retries_limit)
        if raw_game_data is not None:
            transformed_game_data = transform_game_data(raw_game_data, team_ratings)
            load_game_data(team_ratings, transformed_game_data)
            return len(transformed_game_data)
    except Exception as error:
        LogManager.write_log(f"Exception in extract_transform_load... {error}")
        raise Exception(error)

def extract_game_data(start_date: str,
                      end_date: str,
                      retries_limit: int=10) -> DataFrame:
    """Extract game data given a date range. Data is extracted using the hockey_scraper package.
    (https://github.com/HarryShomer/Hockey-Scraper)

    start_date: string for the start date for data extraction
    end_date: string for the end date for data extraction
    retries_limit: Number of retries to extract game data using the hockey_scraper package

    return: DataFrame of an NHL game extracted using the hockey_scraper package
    """
    retrieved = False
    retries = 0

    raw_game_data = None
    while retrieved is False and retries < retries_limit:
        try:
            raw_game_data = hockey_scraper.scrape_schedule(start_date, end_date)
            retrieved = True
        except Exception as error:
            retries += 1
            LogManager.write_log(f"Exception while retrieving data, trying again... {error}")

    return raw_game_data

def transform_game_data(raw_game_data: DataFrame, team_ratings: dict) -> list:
    """Takes raw game data extracted using hockey_scraper and transforms the data with updated
    team ratings and stores it in a list for loading.

    raw_game_data: DataFrame of an NHL game extracted using the hockey_scraper package
    team_ratings: dict where the key is the team name and the value is the team rating

    return: list of Game objects
    """
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

        game_data = initialize_game_data(game, team_ratings)
        if game_data != None:
            transformed_game_data.append(game_data)
    
    return transformed_game_data

def load_game_data(team_ratings: dict, game_data: list) -> None:
    """Update the team ratings and insert the transformed game data in the database.

    team_ratings: dict where the key is the team name and the value is the team rating
    game_data: list of Game objects to be loaded to the database

    return: bool saying if the load was successful
    """
    LogManager.write_log(f"[ETLManager] Loading {len(game_data)} games")
    update_team_ratings(team_ratings)
    insert_game_data(game_data)

def initialize_game_data(game: Game, team_ratings: dict) -> list:
    """Given a Game object, check if the game is valid and return a list of the game
    attributes for loading.

    game: Game object after transformation
    team_ratings: dict where the key is the team name and the value is the team rating

    return: list of game information in the object
    """
    if is_game_valid(game, team_ratings):
        game.calculate_elo(team_ratings[game.home_team], team_ratings[game.away_team])
        team_ratings[game.home_team], team_ratings[game.away_team] = game.home_end_rating, game.away_end_rating
        return game.get_game_information()

def is_game_valid(game: Game, team_ratings: dict) -> bool:
    """Given a Game object, check if the game type and team names are valid.
    """
    return is_game_type_valid(game) and are_teams_valid(game, team_ratings)

def is_game_type_valid(game: Game) -> bool:
    """Check if the game type is valid against a list of valid game types. Game type
    is defined by the hockey_scraper package and can either be a pre-season, season,
    or post-season game.
    """
    return GameType(game.game_type) in valid_game_types

def are_teams_valid(game: Game, team_ratings: dict) -> bool:
    """Check if team names are valid by comparing with the team_ratings dict.
    """
    return (game.home_team in team_ratings and game.away_team in team_ratings)
from datetime import date

from .config import config
from .dbutils import (initialize_database_schema, initialize_team_ratings,
                     get_team_ratings, update_team_ratings, insert_season_update_entry)
from .etlmanager import extract_transform_load
from .logging.logger import LogManager

def initialize_database() -> None:
    """Initialize the database schema if required. update the team ratings and game
    data up to the current date.
    """
    params = config(section="general")
    try:
        initialize_database_schema()
        initialize_team_ratings(float(params['standard_rating']))
        initialize_game_data(params)
    except Exception as error:
        print("Error while initializing the database")

def initialize_game_data(params: dict) -> None:
    """Extract, transform, and load all game data for each season a given start year to
    the current year. When initializing game data we assume that the data is retrieved
    from the API is in the correct order and all games are present.

    params: dict containing required parameters defined in the config file
    """
    start_year = int(params['start_year'])
    if params['simulate']:
        current_year = int(params['simulate_current_year'])
    else:
        current_year = date.datetime.now().year

    team_ratings = get_team_ratings()

    for year in range(start_year, current_year):
        extract_transform_load(start_date=f"{year}-08-01",
                               end_date=f"{year + 1}-08-01",
                               team_ratings=team_ratings,
                               retries_limit=100)
        update_ratings_on_new_season(season_update_id=year,
                                     team_ratings=team_ratings,
                                     standard_rating=float(params['standard_rating']),
                                     carry_over=float(params['carry_over']))

def update_ratings_on_new_season(season_update_id: int,
                                 team_ratings: dict,
                                 standard_rating: float=1500,
                                 carry_over: float=2/3) -> None:
    """Recalculate the team ratings and update the database.

    season_update_id: int for season start year (ex. the 2021-2022 season has the id 2021)
    team_ratings: dict where the key is the team name and the value is the team rating
    standard_rating: float value set as the baseline rating
    carry_over: float value determining the fraction of influence for the current rating
    """
    recalculate_ratings_on_new_season(team_ratings, standard_rating, carry_over)
    
    try:
        update_team_ratings(team_ratings)
        current_date = date.today().strftime("%Y-%m-%d")
        insert_season_update_entry(season_update_id, current_date)
    except Exception as error:
        print("Error while updating the team ratings on new season")

def recalculate_ratings_on_new_season(team_ratings: dict,
                                      standard_rating: float,
                                      carry_over: float) -> None:
    """For each team, apply a formula to adjust the rating closer towards the standard
    
    team_rating: dict where the key is the team name and the value is the team rating
    standard_rating: float value set as the baseline rating
    carry_over: float value determining the fraction of influence for the current rating
    """
    for team, rating in team_ratings.items():
        team_ratings[team] = (1 - carry_over) * standard_rating + (carry_over) * rating
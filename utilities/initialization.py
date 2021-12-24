from datetime import date

from .config import config
from .dbutils import (initialize_database_schema, initialize_team_ratings,
                     get_team_ratings, update_team_ratings, insert_season_update_entry)
from .etlmanager import ETLManager

def initialize_database() -> None:
    params = config(section="general")
    if initialize_database_schema():
        initialize_team_ratings(float(params['standard_rating']))
        initialize_game_data(params)

# When initializing game data we assume that the data is retrieved in the correct order and all games are present
def initialize_game_data(params: dict) -> None:
    start_year = int(params['start_year'])
    if params['simulate']:
        current_year = int(params['simulate_current_year'])
    else:
        current_year = date.datetime.now().year

    team_ratings = get_team_ratings()
    etl_manager = ETLManager(team_ratings)

    for year in range(start_year, current_year):
        etl_manager.extract_transform_load(f"{year}-08-01", f"{year + 1}-08-01", retries_limit=100)
        update_ratings_on_new_season(year, team_ratings, float(params['standard_rating']), float(params['carry_over']))

def update_ratings_on_new_season(season_update_id: int, team_ratings: dict, standard_rating: float=1500, carry_over: float=2/3) -> None:
    recalculate_ratings_on_new_season(team_ratings, standard_rating, carry_over)
    
    if update_team_ratings(team_ratings):
        current_date = date.today().strftime("%Y-%m-%d")
        insert_season_update_entry(season_update_id, current_date)

def recalculate_ratings_on_new_season(team_ratings: dict, standard_rating: float, carry_over: float) -> None:
    for team, rating in team_ratings.items():
        team_ratings[team] = (1 - carry_over) * standard_rating + (carry_over) * rating
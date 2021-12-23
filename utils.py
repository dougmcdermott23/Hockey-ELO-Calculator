from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

import dbutils as db
from config import config
from etlmanager import ETLManager

def initialize_database() -> None:
    params = config(section="general")
    if db.initialize_database_schema():
        db.initialize_team_ratings(float(params['standard_rating']))
        initialize_game_data(params)

# When initializing game data we assume that the data is retrieved in the correct order and all games are present
def initialize_game_data(params: dict) -> None:
    start_year = int(params['start_year'])
    if params['simulate']:
        current_year = int(params['simulate_current_year'])
    else:
        current_year = date.datetime.now().year

    team_ratings = db.get_team_ratings()
    etl_manager = ETLManager(team_ratings)

    for year in range(start_year, current_year):
        etl_manager.extract_transform_load(f"{year}-08-01", f"{year + 1}-08-01", retries_limit=100)
        update_ratings_on_new_season(year, team_ratings, float(params['standard_rating']), float(params['carry_over']))

def update_ratings_on_new_season(season_update_id: int, team_ratings: dict, standard_rating: float=1500, carry_over: float=2/3) -> None:
    recalculate_ratings_on_new_season(team_ratings, standard_rating, carry_over)
    
    if db.update_team_ratings(team_ratings):
        current_date = date.today().strftime("%Y-%m-%d")
        db.insert_season_update_entry(season_update_id, current_date)

def recalculate_ratings_on_new_season(team_ratings: dict, standard_rating: float, carry_over: float) -> None:
    for team, rating in team_ratings.items():
        team_ratings[team] = (1 - carry_over) * standard_rating + (carry_over) * rating

# def PlotTeamHistory(team):
#     years = mdates.YearLocator()
#     months = mdates.MonthLocator()
#     years_fmt = mdates.DateFormatter("%Y")

#     x = [dt.datetime.strptime(d,"%Y-%m-%d").date() for d in team_ratings[team]['date']]
#     y = team_ratings[team]['elo']

#     fig, ax = plt.subplots()
#     ax.plot(x, y)

#     ax.xaxis.set_major_locator(years)
#     ax.xaxis.set_major_formatter(years_fmt)
#     ax.xaxis.set_minor_locator(months)

#     datemin = np.datetime64(team_ratings[team]['date'][0], "Y")
#     datemax = np.datetime64(team_ratings[team]['date'][-1], "Y") + np.timedelta64(1, "Y")
#     ax.set_xlim(datemin, datemax)

#     ax.grid(True)
#     fig.autofmt_xdate()

#     plt.show()
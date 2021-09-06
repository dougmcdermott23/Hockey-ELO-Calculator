from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

import dbutils as db
from config import Config
from etlmanager import ETLManager

def InitializeDatabase():
    params = Config(section='general')
    if db.InitializeDatabaseSchema():
        db.InitializeTeamRatings(params['standard_rating'])
        InitializeGameData(params)

# When initializing game data we assume that the data is retrieved in the correct order and all games are present
def InitializeGameData(params):
    start_year = int(params['start_year'])
    if params['simulate']:
        current_year = int(params['simulate_current_year'])
    else:
        current_year = date.datetime.now().year

    team_ratings = db.GetTeamRatings()
    etl_manager = ETLManager(team_ratings)

    for year in range(start_year, current_year):
        etl_manager.ExtractTransformLoad(f'{year}-08-01', f'{year + 1}-08-01', retries_limit=100)
        UpdateRatingsOnNewSeason(year, team_ratings, float(params['standard_rating']), float(params['carry_over']))

def UpdateRatingsOnNewSeason(season_update_id, team_ratings, standard_rating=1500, carry_over=2/3):
    RecalculateRatingsOnNewSeason(team_ratings, standard_rating, carry_over)
    
    if db.UpdateTeamRatings(team_ratings):
        current_date = date.today().strftime('%Y-%m-%d')
        db.InsertSeasonUpdateEntry(season_update_id, current_date)

def RecalculateRatingsOnNewSeason(team_ratings, standard_rating, carry_over):
    for team, rating in team_ratings.items():
        team_ratings[team] = (1 - carry_over) * standard_rating + (carry_over) * rating

# def PlotTeamHistory(team):
#     years = mdates.YearLocator()
#     months = mdates.MonthLocator()
#     years_fmt = mdates.DateFormatter('%Y')

#     x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in team_ratings[team]['date']]
#     y = team_ratings[team]['elo']

#     fig, ax = plt.subplots()
#     ax.plot(x, y)

#     ax.xaxis.set_major_locator(years)
#     ax.xaxis.set_major_formatter(years_fmt)
#     ax.xaxis.set_minor_locator(months)

#     datemin = np.datetime64(team_ratings[team]['date'][0], 'Y')
#     datemax = np.datetime64(team_ratings[team]['date'][-1], 'Y') + np.timedelta64(1, 'Y')
#     ax.set_xlim(datemin, datemax)

#     ax.grid(True)
#     fig.autofmt_xdate()

#     plt.show()
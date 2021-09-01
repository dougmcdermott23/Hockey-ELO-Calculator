import datetime as dt
import hockey_scraper
import math
from hockey_scraper.utils.shared import season_end_bound
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

import dbutils as db
from game import Game

PRESEASON_GAME_TYPE = 1
SEASON_GAME_TYPE = 2
POSTSEASON_GAME_TYPE = 3

start_year = 2019
standard_rating = 1500
carry_over = 2/3
valid_game_types = [SEASON_GAME_TYPE]

# Used to store team ratings when initializing data for loading
team_ratings = {
    'ANA': standard_rating,
    'ARI': standard_rating,
    'BOS': standard_rating,
    'BUF': standard_rating,
    'CAR': standard_rating,
    'CBJ': standard_rating,
    'CGY': standard_rating,
    'CHI': standard_rating,
    'COL': standard_rating,
    'DAL': standard_rating,
    'DET': standard_rating,
    'EDM': standard_rating,
    'FLA': standard_rating,
    'L.A': standard_rating,
    'MIN': standard_rating,
    'MTL': standard_rating,
    'N.J': standard_rating,
    'NSH': standard_rating,
    'NYI': standard_rating,
    'NYR': standard_rating,
    'OTT': standard_rating,
    'PHI': standard_rating,
    'PIT': standard_rating,
    'S.J': standard_rating,
    'SEA': standard_rating,
    'STL': standard_rating,
    'T.B': standard_rating,
    'TOR': standard_rating,
    'VAN': standard_rating,
    'VGK': standard_rating,
    'WPG': standard_rating,
    'WSH': standard_rating
}

def InitializeDatabase():
    db.InitializeDatabase()

    game_data = SeasonScraper()
    LoadGameData(game_data)

# Load all game data from set starting date to current time
def SeasonScraper():
    current_year = dt.datetime.now().year

    seasons = {}

    for year in range (start_year, current_year):
        retrieved = False
        while retrieved is False:
            try:
                sched_df = hockey_scraper.scrape_schedule(f"{year}-08-01", f"{year + 1}-08-01")
                seasons[year] = sched_df
                retrieved = True
            except:
                print("Exception while retrieving data, trying again...")

    return seasons

def LoadGameData(all_game_data):
    list_of_valid_games = []

    global valid_teams
    valid_teams = db.GetTeamNameInformation()

    current_season = min(all_game_data)

    for season, games in all_game_data.items():
        for index in range(len(games)):
            game = Game(
                games['game_id'][index],
                games['date'][index],
                games['start_time'][index],
                games['venue'][index],
                games['home_team'][index],
                games['away_team'][index],
                games['home_score'][index],
                games['away_score'][index],
                games['status'][index]
                )

            if (season != current_season):
                RecalculateRatingsOnNewSeason()
                current_season = season

            game_information = InitializeGameData(game)
            if game_information != None:
                list_of_valid_games.append(game_information)
    
    db.LoadGameData(list_of_valid_games)
    db.UpdateTeamRatings(team_ratings)

def RecalculateRatingsOnNewSeason():
    for team, rating in team_ratings.items():
        team_ratings[team] = (1 - carry_over) * standard_rating + (carry_over) * rating

def InitializeGameData(game):
    if IsGameValid(game):
        game.CalculateELO(team_ratings[game.home_team], team_ratings[game.away_team])
        team_ratings[game.home_team], team_ratings[game.away_team] = game.home_end_rating, game.away_end_rating
        return game.GetGameInformation()

def IsGameValid(game):
    return IsGameTypeValid(game) and AreTeamsValid(game)

def IsGameTypeValid(game):
    return game.game_type in valid_game_types

def AreTeamsValid(game):
    return (game.home_team in valid_teams and game.away_team in valid_teams)

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
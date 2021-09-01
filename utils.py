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

            if IsGameValid(game):
                game.CalculateELO(team_ratings[game.home_team], team_ratings[game.away_team])
                team_ratings[game.home_team], team_ratings[game.away_team] = game.home_end_rating, game.away_end_rating
                list_of_valid_games.append(game.GetGameInformation())
    
    db.LoadGameData(list_of_valid_games)
    db.UpdateTeamRatings(team_ratings)

def IsGameValid(game):
    return IsGameTypeValid(game) and AreTeamsValid(game)

def IsGameTypeValid(game):
    return game.game_type in valid_game_types

def AreTeamsValid(game):
    return (game.home_team in valid_teams and game.away_team in valid_teams)

# def GenerateELO(historic_data):
#     for season, games in historic_data.items():
#         for game in range(len(games)):
#             valid, home_team, away_team = ValidateGame(games['home_team'][game], games['away_team'][game])
#             if (valid):
#                 date = games['date'][game]
#                 home_score = games['home_score'][game]
#                 away_score = games['away_score'][game]
#                 CalculateELO(home_team, away_team, season, date, game, home_score, away_score)

#         # Adjust team elo's after the season is over
#         RecalculateOnSeasonOver(season + 1)

#     PlotTeamHistory('TOR')

#     return

# def CalculateELO(home_team, away_team, season, date, game_number, home_score, away_score):
#     K = 20
#     R_home = team_ratings[home_team]['elo'][-1]
#     R_away = team_ratings[away_team]['elo'][-1]
#     S_home = 0
#     S_away = 0

#     if home_score > away_score:
#         S_home = 1

#     S_away = 1 - S_home

#     # Expected Score
#     Q_home = math.pow(10, R_home/400)
#     Q_away = math.pow(10, R_away/400)
#     E_home = Q_home / (Q_home + Q_away)
#     E_away = Q_away / (Q_home + Q_away)

#     # Updated Rating
#     R_home_new = R_home + K * (S_home - E_home)
#     R_away_new = R_away + K * (S_away - E_away)

#     # Store new Team Rating
#     StoreTeamInformation(home_team, season, date, game_number, R_home_new)
#     StoreTeamInformation(away_team, season, date, game_number, R_away_new)
#     return

# def RecalculateOnSeasonOver(new_season):
#     carry_over = 2/3
    
#     for team in team_ratings:
#         new_elo = (1 - carry_over) * standard_rating + (carry_over) * team_ratings[team]['elo'][-1]
#         StoreTeamInformation(team, new_season, '{}-09-30'.format(new_season), None, new_elo)

# def StoreTeamInformation(team, season, date, game_number, elo):
#     team_ratings[team]['season'].append(season)
#     team_ratings[team]['date'].append(date)
#     team_ratings[team]['game_number'].append(game_number)
#     team_ratings[team]['elo'].append(elo)
#     return

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
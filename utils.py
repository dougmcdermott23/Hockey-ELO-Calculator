import hockey_scraper
import math
import pdb
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

start_year = 2005
standard_rating = 1500

team_ratings = {
    'ANA': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'ARI': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'BOS': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'BUF': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'CAR': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'CBJ': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'CGY': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'CHI': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'COL': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'DAL': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'DET': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'EDM': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'FLA': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'L.A': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'MIN': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'MTL': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'N.J': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'NSH': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'NYI': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'NYR': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'OTT': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'PHI': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'PIT': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'S.J': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'STL': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'T.B': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'TOR': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'VAN': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'VGK': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'WPG': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]},
    'WSH': {'season': [start_year], 'date': ['{}-09-30'.format(start_year)], 'game_number': [None], 'elo': [standard_rating]}
}

def SeasonScraper():
    current_year = dt.datetime.now().year

    seasons = {}

    for year in range (start_year, current_year):
        retrieved = False
        while retrieved is False:
            try:
                sched_df = hockey_scraper.scrape_schedule("{}-10-01".format(year), "{}-07-01".format(year + 1))
                seasons[year] = sched_df
                retrieved = True
            except:
                print("Exception")

    return seasons

def ValidateGame(home_team, away_team):
    if home_team == 'PHX':
        home_team = 'ARI'

    if away_team == 'PHX':
        away_team = 'ARI'

    if home_team == 'ATL':
        home_team = 'WPG'

    if away_team == 'ATL':
        away_team = 'WPG'

    if home_team in team_ratings and away_team in team_ratings:
        return True, home_team, away_team
    else:
        return False, home_team, away_team

def GenerateELO(historic_data):
    for season, games in historic_data.items():
        for game in range(len(games)):
            valid, home_team, away_team = ValidateGame(games['home_team'][game], games['away_team'][game])
            if (valid):
                date = games['date'][game]
                home_score = games['home_score'][game]
                away_score = games['away_score'][game]
                CalculateELO(home_team, away_team, season, date, game, home_score, away_score)

        # Adjust team elo's after the season is over
        RecalculateOnSeasonOver(season + 1)

    PlotTeamHistory('TOR')

    return

def CalculateELO(home_team, away_team, season, date, game_number, home_score, away_score):
    K = 20
    R_home = team_ratings[home_team]['elo'][-1]
    R_away = team_ratings[away_team]['elo'][-1]
    S_home = 0
    S_away = 0

    if home_score > away_score:
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

    # Store new Team Rating
    StoreTeamInformation(home_team, season, date, game_number, R_home_new)
    StoreTeamInformation(away_team, season, date, game_number, R_away_new)
    return

def RecalculateOnSeasonOver(new_season):
    carry_over = 2/3
    
    for team in team_ratings:
        new_elo = (1 - carry_over) * standard_rating + (carry_over) * team_ratings[team]['elo'][-1]
        StoreTeamInformation(team, new_season, '{}-09-30'.format(new_season), None, new_elo)

def StoreTeamInformation(team, season, date, game_number, elo):
    team_ratings[team]['season'].append(season)
    team_ratings[team]['date'].append(date)
    team_ratings[team]['game_number'].append(game_number)
    team_ratings[team]['elo'].append(elo)
    return

def PlotTeamHistory(team):
    years = mdates.YearLocator()
    months = mdates.MonthLocator()
    years_fmt = mdates.DateFormatter('%Y')

    x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in team_ratings[team]['date']]
    y = team_ratings[team]['elo']

    fig, ax = plt.subplots()
    ax.plot(x, y)

    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(years_fmt)
    ax.xaxis.set_minor_locator(months)

    datemin = np.datetime64(team_ratings[team]['date'][0], 'Y')
    datemax = np.datetime64(team_ratings[team]['date'][-1], 'Y') + np.timedelta64(1, 'Y')
    ax.set_xlim(datemin, datemax)

    ax.grid(True)
    fig.autofmt_xdate()

    plt.show()
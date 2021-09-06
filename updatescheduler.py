from datetime import date, datetime, timedelta
import schedule
import time

from config import Config
from etlmanager import ETLManager
from utils import UpdateRatingsOnNewSeason
import dbutils as db

last_update_date = None
current_date = None

# Initialize the schedule for the update thread
def InitializeDailyGameDataUpdateScheduler():
    params = Config(section='general')
    if params['simulate']:
        schedule.every(int(params['simulate_update_game_date_interval'])).seconds.do(SimulateUpdateDailyGameData)
        run_pending_check_interval = int(params['simulate_run_pending_check_interval'])
        InitializeSimulate(params['simulate_current_year'])
    else:
        schedule.every().day.at('05:00').do(UpdateDailyGameData)
        run_pending_check_interval = int(params['run_pending_check_interval'])

    while True:
        schedule.run_pending()
        time.sleep(run_pending_check_interval)

# Extracts, transforms, and loads all game data from the previous update to now
def UpdateDailyGameData():
    print("[UpdateScheduler] Starting Daily Game Update")
    last_update_date = GetLastUpdateDay()
    current_date = date.today().strftime('%Y-%m-%d')

    etl_manager = ETLManager()
    etl_manager.ExtractTransformLoad(last_update_date, current_date)
    
    CheckSeasonEndUpdate(current_date)
    print("[UpdateScheduler] Finished Daily Game Update")

# Get the most recent game date in DB and return as string
def GetLastUpdateDay():
    last_day = db.GetLastGameDate()[0] + timedelta(days=1)
    return last_day.strftime('%Y-%m-%d')

# Check if season update has occurred. If it hasn't and it is time to update, recalculate team ratings and update
def CheckSeasonEndUpdate(current_date):
    params = Config(section='general')
    reset_month = int(params['season_reset_month'])
    current_month = datetime.strptime(current_date, '%Y-%m-%d').date().month

    if current_month == reset_month:
        current_year = datetime.strptime(current_date, '%Y-%m-%d').date().year - 1
        if not db.HasSeasonUpdateOccurred(current_year):
            print("[UpdateScheduler] Recalculating ratings on season end")
            team_ratings = db.GetTeamRatings()
            params = Config(section='general')
            UpdateRatingsOnNewSeason(current_year, team_ratings, params['standard_rating'], params['carry_over'])

# SIMULATE: Used to initialize the values for simulation
def InitializeSimulate(simulate_current_year):
    global last_update_date
    global current_date

    last_update_date = GetLastUpdateDay()
    current_date = simulate_current_year + '-07-30'
    if last_update_date > current_date:
        current_date = (db.GetLastGameDate()[0] + timedelta(days=2)).strftime('%Y-%m-%d')

# SIMULATE: Extracts, transforms, and loads all game data from the previous update to now
def SimulateUpdateDailyGameData():
    print("[UpdateScheduler] Starting Simulate Daily Game Update")
    last_update_date = GetLastUpdateDay()

    etl_manager = ETLManager()
    etl_manager.ExtractTransformLoad(last_update_date, current_date)

    CheckSeasonEndUpdate(current_date)
    UpdateTestingDates()
    print("[UpdateScheduler] Finished Simulate Daily Game Update")

# SIMULATE: Update the current date used for simulation
def UpdateTestingDates():
    global current_date
    
    next_day = datetime.strptime(current_date, '%Y-%m-%d') + timedelta(days=1)
    current_date = next_day.strftime('%Y-%m-%d')
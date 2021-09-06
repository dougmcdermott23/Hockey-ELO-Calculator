from datetime import date, datetime, timedelta
import schedule
import time

from config import Config
from etlmanager import ETLManager
from utils import UpdateRatingsOnNewSeason
import dbutils as db

class UpdateScheduler:
    def __init__(self):
        self.params = Config(section='general')
        if self.params['simulate']:
            schedule.every(int(self.params['simulate_update_game_date_interval'])).seconds.do(self.SimulateUpdateDailyGameData)
            self.run_pending_check_interval = int(self.params['simulate_run_pending_check_interval'])
            self.InitializeSimulate(self.params['simulate_current_year'])
        else:
            schedule.every().day.at('05:00').do(self.UpdateDailyGameData)
            self.run_pending_check_interval = int(self.params['run_pending_check_interval'])

    def CheckForPendingUpdates(self):
        while True:
            schedule.run_pending()
            time.sleep(self.run_pending_check_interval)

    # Extracts, transforms, and loads all game data from the previous update to now
    def UpdateDailyGameData(self):
        print("[UpdateScheduler] Starting Daily Game Update")
        last_update_date = self.GetLastUpdateDay()
        current_date = date.today().strftime('%Y-%m-%d')

        etl_manager = ETLManager()
        etl_manager.ExtractTransformLoad(last_update_date, current_date)
        
        self.CheckSeasonEndUpdate(current_date)
        print("[UpdateScheduler] Finished Daily Game Update")

    # Get the most recent game date in DB and return as string
    def GetLastUpdateDay(self):
        last_day = db.GetLastGameDate()[0] + timedelta(days=1)
        return last_day.strftime('%Y-%m-%d')

    # Check if season update has occurred. If it hasn't and it is time to update, recalculate team ratings and update
    def CheckSeasonEndUpdate(self, current_date):
        params = Config(section='general')
        reset_month = int(params['season_reset_month'])
        current_month = datetime.strptime(current_date, '%Y-%m-%d').date().month

        if current_month == reset_month:
            current_year = datetime.strptime(current_date, '%Y-%m-%d').date().year - 1
            if not db.HasSeasonUpdateOccurred(current_year):
                print("[UpdateScheduler] Recalculating ratings on season end")
                team_ratings = db.GetTeamRatings()
                params = Config(section='general')
                UpdateRatingsOnNewSeason(current_year, team_ratings, float(params['standard_rating']), float(params['carry_over']))

    #########################################################
    # SIMULATION
    #########################################################

    # Used to initialize the values for simulation
    def InitializeSimulate(self, simulate_current_year):
        last_update_date = self.GetLastUpdateDay()
        self.simulate_current_date = simulate_current_year + '-09-25'
        if last_update_date > self.simulate_current_date:
            current_date = (db.GetLastGameDate()[0] + timedelta(days=2)).strftime('%Y-%m-%d')

    # Extracts, transforms, and loads all game data from the previous update to now
    def SimulateUpdateDailyGameData(self):
        print("[UpdateScheduler] Starting Simulate Daily Game Update")
        last_update_date = self.GetLastUpdateDay()

        etl_manager = ETLManager()
        etl_manager.ExtractTransformLoad(last_update_date, self.simulate_current_date)

        self.CheckSeasonEndUpdate(self.simulate_current_date)
        self.UpdateTestingDates()
        print("[UpdateScheduler] Finished Simulate Daily Game Update")

    # Update the current date used for simulation
    def UpdateTestingDates(self):
        next_day = datetime.strptime(self.simulate_current_date, '%Y-%m-%d') + timedelta(days=1)
        self.simulate_current_date = next_day.strftime('%Y-%m-%d')
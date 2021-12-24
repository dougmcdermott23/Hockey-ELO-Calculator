from datetime import date, datetime, timedelta
import schedule
import time

from .config import config
from .dbutils import (get_last_game_date, has_season_update_occurred, get_team_ratings)
from .etlmanager import ETLManager
from .initialization import update_ratings_on_new_season

# Break into a base class and derived classes for normal and simulation
# Or this shouldn't be a class...
# Maybe the same with ETL
class UpdateScheduler: 
    def __init__(self) -> None:
        self.params = config(section="general")
        if self.params['simulate']:
            schedule.every(int(self.params['simulate_update_game_date_interval'])).seconds.do(self.simulate_update_daily_game_data)
            self.run_pending_check_interval = int(self.params['simulate_run_pending_check_interval'])
            self.initialize_simulate(self.params['simulate_current_year'])
        else:
            schedule.every().day.at("05:00").do(self.update_daily_game_data)
            self.run_pending_check_interval = int(self.params['run_pending_check_interval'])

    def check_for_pending_updates(self) -> None:
        while True:
            schedule.run_pending()
            time.sleep(self.run_pending_check_interval)

    # Extracts, transforms, and loads all game data from the previous update to now
    def update_daily_game_data(self) -> None:
        print("[UpdateScheduler] Starting Daily Game Update")
        last_update_date = self.get_last_update_day()
        current_date = date.today().strftime("%Y-%m-%d")

        etl_manager = ETLManager()
        etl_manager.extract_transform_load(last_update_date, current_date)
        
        self.check_season_end_update(current_date)
        print("[UpdateScheduler] Finished Daily Game Update")

    # Get the most recent game date in DB and return as string
    def get_last_update_day(self) -> str:
        last_day = get_last_game_date() + timedelta(days=1)
        return last_day.strftime("%Y-%m-%d")

    # Check if season update has occurred. If it hasn't and it is time to update, recalculate team ratings and update
    def check_season_end_update(self, current_date: str) -> None:
        params = config(section="general")
        reset_month = int(params['season_reset_month'])
        current_month = datetime.strptime(current_date, "%Y-%m-%d").date().month

        if current_month == reset_month:
            current_year = datetime.strptime(current_date, "%Y-%m-%d").date().year - 1
            if not has_season_update_occurred(current_year):
                print("[UpdateScheduler] Recalculating ratings on season end")
                team_ratings = get_team_ratings()
                params = config(section="general")
                update_ratings_on_new_season(current_year, team_ratings, float(params['standard_rating']), float(params['carry_over']))

    #########################################################
    # SIMULATION METHODS BELOW
    #########################################################

    # Used to initialize the values for simulation
    def initialize_simulate(self, simulate_current_year: str) -> None:
        last_update_date = self.get_last_update_day()
        self.simulate_current_date = simulate_current_year + "-09-25"
        if last_update_date > self.simulate_current_date:
            current_date = (get_last_game_date() + timedelta(days=2)).strftime("%Y-%m-%d")

    # Extracts, transforms, and loads all game data from the previous update to now
    def simulate_update_daily_game_data(self) -> None:
        print("[UpdateScheduler] Starting Simulate Daily Game Update")
        last_update_date = self.get_last_update_day()

        etl_manager = ETLManager()
        etl_manager.extract_transform_load(last_update_date, self.simulate_current_date)

        self.check_season_end_update(self.simulate_current_date)
        self.update_testing_dates()
        print("[UpdateScheduler] Finished Simulate Daily Game Update")

    # Update the current date used for simulation
    def update_testing_dates(self) -> None:
        next_day = datetime.strptime(self.simulate_current_date, "%Y-%m-%d") + timedelta(days=1)
        self.simulate_current_date = next_day.strftime("%Y-%m-%d")
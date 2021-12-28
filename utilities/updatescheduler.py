import schedule
import time

from datetime import date, datetime, timedelta
from schedule import Job

from .dbutils import (get_last_game_date, has_season_update_occurred, get_team_ratings)
from .etlmanager import extract_transform_load
from .initialization import update_ratings_on_new_season

# TODO: resolve the inf while loop in update_scheduler

class UpdateScheduler:
    """Daily updates"""
    simulate: bool
    pending_check_interval_sec: float
    update_schedule: Job
    simulate_offset: int

    """Updating on season end"""
    reset_month: int
    standard_rating: float
    carry_over: float

    def __init__(self, params: dict) -> None:
        """Daily updates"""
        self.simulate: bool = params["simulate"]
        self.pending_check_interval_sec: float = float(params["simulate_pending_check_interval_sec"] if self.simulate
                                                       else params["pending_check_interval_sec"])
        self.update_schedule: Job = schedule.every(int(params["simulate_update_game_date_interval_sec"])).seconds if self.simulate \
                                    else schedule.every().day.at(f"{params['game_data_update_time']}")
        self.simulate_offset = 1

        """Updating on season end"""
        self.reset_month = int(params['season_reset_month'])
        self.standard_rating = float(params['standard_rating'])
        self.carry_over = float(params['carry_over'])

    def update_scheduler(self) -> None:
        """Initialize update schedule and periodically check if an update is ready.
        """
        self.update_schedule.do(self.update_daily_game_data)

        while True:
            schedule.run_pending()
            time.sleep(self.pending_check_interval_sec)

    def update_daily_game_data(self) -> None:
        """Get the start and end date for the ETL process. Perform the ETL process and
        then check if an end of season update is required.
        """
        print("[UpdateScheduler] Starting Daily Game Update")
        start_date, end_date = self.get_update_dates()

        num_games = extract_transform_load(start_date=start_date, end_date=end_date)

        if self.simulate and num_games > 0:
            self.simulate_offset = 1
        
        self.check_season_end_update(end_date)
        print("[UpdateScheduler] Finished Daily Game Update")

    def get_update_dates(self) -> None:
        """Query the database are return the start and end date for data extraction. The
        start and end dates are inclusive for the hockey_scraper package.
        """
        start_date = self.get_next_update_date()
        end_date = date.today().strftime("%Y-%m-%d")

        if self.simulate:
            end_date = self.get_next_update_date(self.simulate_offset)
            self.simulate_offset += 1
        
        return start_date, end_date

    def get_next_update_date(self, offset: int = 1) -> str:
        """The start date for extracting game data is inclusive. Get the last stored game date
        from the database and return the next date in the proper string format.

        offset: Number of days to add to the date of the last game loaded in the database

        return: Date string in the format YYYY-mm-dd
        """
        last_day = get_last_game_date() + timedelta(days=offset)
        return last_day.strftime("%Y-%m-%d")

    def check_season_end_update(self, date: str) -> None:
        """Check if the current month is equal to the reset month. If the reset has not happened
        yet, calculate the new team ratings and load into the database.

        date: Current date to check against the reset month
        """
        current_month = datetime.strptime(date, "%Y-%m-%d").date().month

        if current_month == self.reset_month:
            current_year = datetime.strptime(date, "%Y-%m-%d").date().year - 1
            if not has_season_update_occurred(current_year):
                print("[UpdateScheduler] Recalculating ratings on season end")
                team_ratings = get_team_ratings()
                update_ratings_on_new_season(season_update_id=current_year,
                                             team_ratings=team_ratings,
                                             standard_rating=self.standard_rating,
                                             carry_over=self.carry_over)
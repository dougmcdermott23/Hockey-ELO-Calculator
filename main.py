import sys
import threading

from utilities.config import config
from utilities.initialization import initialize_database
from utilities.logging.logger import LogManager
from utilities.updatescheduler import UpdateScheduler

def main() -> None:
    initialize_database()

    params = config(section="general")
    update_scheduler = UpdateScheduler(params)
    update_scheduler_thread = threading.Thread(target=update_scheduler.update_scheduler())
    update_scheduler_thread.start()

    input_thread = threading.Thread(target=process_input())
    input_thread.start()

    # TODO End threads if necessary and wait before quitting
    update_scheduler_thread.join()
    input_thread.join()

    logger.close_log()

def process_input() -> None:
    while True:
        val = input("Enter 1 to access accounts, enter 2 to create a trade: ")

        if val == "1":
            logger.log_message("Accounts")
        if val == "2":
            logger.log_message("Trades")

if __name__ == '__main__':
    main()
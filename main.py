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

    input_thread = threading.Thread(target=process_input(), name="input_thread")
    input_thread.start()

    # TODO End threads if necessary and wait before quitting
    input_thread.join()
    update_scheduler.close_update_scheduler()

    LogManager.close_log()

def process_input() -> None:
    stopped = False
    while not stopped:
        val = input("Enter 0 to exit: ")

        if val == "0":
            stopped = True

if __name__ == '__main__':
    main()
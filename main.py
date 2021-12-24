import sys
import threading

from utilities.updatescheduler import UpdateScheduler
from utilities.initialization import initialize_database

def main(argv) -> None:
    initialize_database()

    # Start an update thread
    update_scheduler = UpdateScheduler()
    update_scheduler_thread = threading.Thread(target=update_scheduler.check_for_pending_updates)
    update_scheduler_thread.start()

    process_input()

def process_input() -> None:
    while True:
        val = input("Enter 1 to access accounts, enter 2 to create a trade: ")

        if val == "1":
            print("Accounts")
        if val == "2":
            print("Trades")

if __name__ == '__main__':
    main(sys.argv)
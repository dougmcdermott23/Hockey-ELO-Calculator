import sys
import time
import threading

import utils
from updatescheduler import UpdateScheduler

def main(argv) -> None:
    utils.InitializeDatabase()

    # Start an update thread
    update_scheduler = UpdateScheduler()
    update_scheduler_thread = threading.Thread(target=update_scheduler.CheckForPendingUpdates)
    update_scheduler_thread.start()

    ProcessInput()

def ProcessInput() -> None:
    while True:
        val = input("Enter 1 to access accounts, enter 2 to create a trade: ")

        if val == '1':
            print("Accounts")
        if val == '2':
            print("Trades")

if __name__ == '__main__':
    main(sys.argv)
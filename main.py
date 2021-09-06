import sys
import time
import threading

import utils
from updatescheduler import UpdateScheduler

def main(argv):
    utils.InitializeDatabase()

    # Start an update thread
    update_scheduler = UpdateScheduler()
    update_scheduler_thread = threading.Thread(target=update_scheduler.CheckForPendingUpdates())
    update_scheduler_thread.start()

    ProcessMessages()

def ProcessMessages():
    while True:
        time.sleep(60)

if __name__ == '__main__':
    main(sys.argv)
import sys
import time
import threading

import utils
from updatescheduler import InitializeDailyGameDataUpdateScheduler

def main(argv):
    utils.InitializeDatabase()

    # Start an update thread
    update_scheduler_thread = threading.Thread(target=InitializeDailyGameDataUpdateScheduler)
    update_scheduler_thread.start()

    ProcessMessages()

def ProcessMessages():
    while True:
        time.sleep(60)

if __name__ == '__main__':
    main(sys.argv)
import logging
import os

from datetime import datetime
from multiprocessing import Process, Queue
from pathlib import Path
from typing import Any

from utilities.config import config
from .logmessage import LogMessage

TERMINATE_MESSAGE = 'done'

class LogManager:
    __instance = None
    
    logging_enabled: bool
    log_file_path: Path
    logger_name: str
    logger_level: int
    logger_format: str
    logger_queue: Queue
    logger: logging.Logger
    logger_process: Process

    @staticmethod
    def get_instance():
        if LogManager.__instance is None:
            LogManager()
        return LogManager.__instance

    @staticmethod
    def write_log(log_message: Any) -> None:
        instance = LogManager.get_instance()
        instance.logger_queue.put(log_message)

    @staticmethod
    def close_log() -> None:
        instance = LogManager.get_instance()
        if instance.logger_process is not None:
            instance.logger_queue.put(TERMINATE_MESSAGE)
            instance.logger_process.join()

    def __init__(self):
        if LogManager.__instance is not None:
            raise Exception("This class is a singleton, use get_instance to get an instance of this class.")
        else:
            params = config(section="logging")

            self.log_file_path = Path(params['log_file_path'], params['log_file_name']).with_suffix('.log')
            self.logging_enabled = os.path.isfile(self.log_file_path)
            self.logger_name = params['logger_name']
            self.logger_level = logging._nameToLevel[params['logger_level']]
            self.logger_format = '%(message)s'

            self.logger_queue = Queue()
            self.logger = logging.getLogger(self.logger_name)
            self.logger_process = Process(target=self.process_logger_queue)

            self.logger_process.start()

            LogManager.__instance = self

    def configure_logger(self) -> None:
        handlers = []

        if self.logging_enabled:
            handlers.append(logging.FileHandler(self.log_file_path))
        else:
            handlers.append(logging.StreamHandler())

        logging.basicConfig(level=self.logger_level,
                            format=self.logger_format,
                            handlers=handlers)

    def process_logger_queue(self) -> None:
        self.configure_logger()

        while True:
            input = self.logger_queue.get()

            if isinstance(input, str):
                if input == TERMINATE_MESSAGE:
                    break
                else:
                    date_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                    message = f"<{date_time}> {input}"
                    self.logger.info(message)
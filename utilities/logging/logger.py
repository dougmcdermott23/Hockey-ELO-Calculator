import logging

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

    def __init__(self):
        if LogManager.__instance is not None:
            raise Exception("This class is a singleton, use get_instance to get an instance of this class.")
        else:
            params = config(section="logging")

            self.logging_enabled = params['logging_enabled'] == "True" or params['logging_enabled'] == "true"
            self.log_file_path = Path(params['log_file_path'], params['log_file_name']).with_suffix('.log')
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
                    self.logger.info(input)

    def log_message(self, log_message: Any) -> None:
        self.logger_queue.put(log_message)

    def close_log(self) -> None:
        if self.logger_process is not None:
            self.logger_queue.put(TERMINATE_MESSAGE)
            self.logger_process.join()
import logging

from multiprocessing import Process, Queue
from pathlib import Path

from LogMessage import LogMessage

TERMINATE_MESSAGE = 'done'

class LoggerObject:
    log_file_path: Path
    logging_enabled: bool
    logger_message_type: LogMessage
    logger_name: str
    logger_level: int
    logger_formatter: str
    logger_queue: Queue
    logger_process: Process

    def __init__(self,
                 log_file_path: Path = '',
                 logger_message_type: LogMessage = None,
                 logger_name: str = None,
                 logger_level: int = logging.INFO,
                 logger_formatter: str = '%(message)s') -> None:
        self.log_file_path = log_file_path
        self.logging_enabled = False if not log_file_path else True
        self.logger_message_type = logger_message_type
        self.logger_name = logger_name
        self.logger_level = logger_level
        self.logger_formatter = logger_formatter
        self.logger_queue = Queue()
        self.logger = logging.getLogger(logger_name)
        self.logger_process = Process(target=self.process_logger_queue)

        self.logger_process.start

    def configure_logger(self) -> None:
        handlers = []

        if self.logging_enabled:
            handlers.append(logging.FileHandler(self.log_file_path))
        else:
            handlers.append(logging.StreamHandler())

        logging.basicConfig(level=self.logger_level,
                            format=self.logger_formatter,
                            handlers=handlers)

        if self.logger_message_type is not None:
            self.logger.info(self.logger_message_type.get_log_header())

    def process_logger_queue(self) -> None:
        self.configure_logger()

        while True:
            input = self.logger_queue.get()

            if isinstance(input, str) and input == TERMINATE_MESSAGE:
                break

    def close_log(self) -> None:
        if self.logger_process is not None:
            self.logger_queue.put(TERMINATE_MESSAGE)
            self.logger_process.join()
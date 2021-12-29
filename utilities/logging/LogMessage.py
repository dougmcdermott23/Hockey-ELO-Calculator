from abc import ABC, abstractmethod

from .enums import LogSeverity

class LogMessage(ABC):
    @abstractmethod
    def __init__(self,
               log_name: str = "",
               log_severity: LogSeverity = LogSeverity.NONE) -> None:
        self.log_name = log_name
        self.log_severity = log_severity

    @abstractmethod
    def __str__(self) -> str:
        return(f"{self.log_name},{self.log_severity},")

    @staticmethod
    @abstractmethod
    def get_log_header() -> str:
        return (f"log_name,log_severity,")
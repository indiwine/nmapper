import uuid
from datetime import datetime

from scanner.history.abstractsnapshot import AbstractSnapshot


class ScanSnapshot(AbstractSnapshot):
    def __init__(self, scan_result: dict):
        self._date = datetime.now()
        self._scan_result = scan_result
        self._name = f'{uuid.uuid4()}-{self._date.timestamp()}'

    def get_time(self) -> str:
        return str(self._date.timestamp())

    def get_name(self) -> str:
        return self._name

    def get_state(self):
        return self._scan_result

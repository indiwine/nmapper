import os
from abc import ABC, abstractmethod
from typing import List

from scanner import ScanResult


class BasicFormatter(ABC):

    def __init__(self, render_dir):
        self.render_dir = render_dir

    def filter_hosts(self, hosts: List[ScanResult]) -> List[ScanResult]:
        return hosts

    @staticmethod
    def get_file_dir(file) -> str:
        return os.path.dirname(os.path.realpath(file))

    @abstractmethod
    def render(self, hosts: List[ScanResult]):
        pass

from typing import List

from scanner import ScanResult


class BasicFormatter:

    def __init__(self, render_dir):
        self.render_dir = render_dir

    def filter_hosts(self, hosts: List[ScanResult]) -> List[ScanResult]:
        return hosts

    def render(self, hosts: List[ScanResult]):
        pass
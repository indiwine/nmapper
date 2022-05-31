import os.path
import pathlib
from typing import List

from jinja2 import Environment, FileSystemLoader

from formatter import BasicFormatter
from scanner import ScanResult


class DiscoveredHostsFormatter(BasicFormatter):

    def __init__(self, render_dir):
        super().__init__(render_dir)
        self._jinja_env = Environment(
            loader=FileSystemLoader([os.path.join(pathlib.Path(__file__).parent.resolve())]),
            extensions=['jinja2.ext.debug']
        )

    def filter_hosts(self, hosts: List[ScanResult]) -> List[ScanResult]:
        return list(filter(lambda item: item.is_up and item.has_tcp, hosts))

    def render(self, hosts: List[ScanResult]):
        self._jinja_env.get_template('template.jinja2').stream(hosts=hosts).dump(
            os.path.join(self.render_dir, 'scan.txt'))

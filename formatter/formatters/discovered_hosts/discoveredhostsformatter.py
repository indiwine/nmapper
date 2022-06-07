import os.path
import pathlib
from distutils.dir_util import copy_tree
from typing import List

from jinja2 import Environment, FileSystemLoader

from formatter.formatters.basicformatter import BasicFormatter
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
        copy_tree(os.path.join(self.get_file_dir(__file__), 'assets'), os.path.join(self.render_dir, 'assets'))
        hosts_by_page = list(self._chunks(hosts, 20))
        total_pages = len(hosts_by_page)-1

        for i, hosts_chunk in enumerate(hosts_by_page):
            file_name = os.path.join(self.render_dir, 'index.html' if i == 0 else f'page-{i}.html')
            pages=self._calc_pages(i, total_pages)
            self._jinja_env.get_template('template.jinja2').stream(
                hosts=hosts_chunk,
                pages=pages
            ).dump(file_name)


    def _calc_pages(self, current_idx: int, total: int):
        return {
            'previous': self._get_previous_page(current_idx, total),
            'next': self._get_next_page(current_idx, total),
            'pages': self.get_pages(current_idx, total)
        }

    def get_pages(self, current_idx: int, total: int):
        result = []
        for i in range(0, total+1):
            result.append({
                "title": i+1,
                "page": 'index.html' if i == 0 else f'page-{i}.html',
                "active": current_idx == i
            })
        return result


    def _get_previous_page(self, current_idx: int, total: int):
        if current_idx == 0:
            return None
        elif current_idx == 1:
            return 'index.html'
        else:
            return f'page-{current_idx-1}.html'

    def _get_next_page(self, current_idx: int, total: int):
        return None if current_idx == total else f'page-{current_idx+1}.html'

    @staticmethod
    def _chunks(lst: list, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

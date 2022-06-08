import json
import logging
import os
import socket
from datetime import datetime
from typing import List, Dict, Type

from formatter.formatters.basicformatter import BasicFormatter
from scanner import ScanResult
from .formatters.acunetix_import.acunetiximportformatter import AcunetixImportFormatter
from .formatters.discovered_hosts.discoveredhostsformatter import DiscoveredHostsFormatter

_formatter_map: Dict[str, Type[BasicFormatter]] = {
    'discovered-hosts': DiscoveredHostsFormatter,
    'acunetix-import': AcunetixImportFormatter
}


class FormatterManager:
    def __init__(self, scan_results: List[ScanResult]):
        self.scan_results = scan_results
        now = datetime.now()
        self._basic_dir = f'{os.getcwd()}/scan-{now.strftime("%d-%m-%Y-%H%M%S")}'
        logging.debug(f'Creating scan dir: {self._basic_dir}')
        os.mkdir(self._basic_dir)
        self._sort_results()

    def _sort_results(self):
        self.scan_results.sort(key=lambda item: socket.inet_aton(item.host))

    def save_json_results(self):
        with open(os.path.join(self._basic_dir, 'raw_results.json'), 'w') as outfile:
            json.dump(list(map(lambda item: item.raw_dict, self.scan_results)), outfile, indent=4)

    def output(self):
        for formatter_name, formatter_class in _formatter_map.items():
            logging.debug(f'Outputting result using formatter {formatter_name}')
            formatter_dir = os.path.join(self._basic_dir, formatter_name)
            os.mkdir(formatter_dir)
            logging.debug(f'Dir created: {formatter_dir}')
            formatter_inst = formatter_class(formatter_dir)
            formatter_inst.render(formatter_inst.filter_hosts(self.scan_results))
            logging.debug(f'Output formatter "{formatter_name}" done rendering!')

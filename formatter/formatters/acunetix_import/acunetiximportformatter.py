import csv
import os.path
import re
from typing import List

from formatter.formatters.basicformatter import BasicFormatter
from scanner import ScanResult


class AcunetixImportFormatter(BasicFormatter):

    def filter_hosts(self, hosts: List[ScanResult]) -> List[ScanResult]:
        return list(filter(lambda item: item.is_up and item.has_http_service, hosts))

    def render(self, hosts: List[ScanResult]):
        regex = r"http(s)?"
        csv_file = open(os.path.join(self.render_dir, 'import.csv'), 'w', newline='')
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(['Address', 'Description'])
        for host in hosts:
            for port, port_definition in host.tcp.items():
                match = re.search(regex, port_definition['name'])
                if match is not None:
                    csv_writer.writerow([
                        f'{match.group()}://{host.host}:{port}',
                        f'Automatically generated import for {host.host}:{port}, {port_definition["name"]}'
                    ])
        csv_file.close()

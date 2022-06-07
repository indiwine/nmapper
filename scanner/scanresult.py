import hashlib
import re

from scanner.history.abstractsnapshot import AbstractSnapshot


class ScanResult:
    @staticmethod
    def wrap(results_list: list):
        return list(map(lambda item: ScanResult(item), results_list))

    @staticmethod
    def restore(snapshot: AbstractSnapshot):
        return ScanResult(snapshot.get_state())

    def __init__(self, raw_result: dict):
        self._raw_result = raw_result

    @property
    def raw_dict(self):
        return self._raw_result

    @property
    def host(self) -> str:
        return self._raw_result['host']

    @property
    def host_hash(self) -> str:
        return hashlib.md5(self.host.encode()).hexdigest()

    @property
    def is_success(self) -> bool:
        return self._raw_result['success']

    @property
    def is_up(self):
        return self.is_success and self.nmap_scan_stats['uphosts'] == '1'

    @property
    def nmap_scan_stats(self) -> dict:
        return self._raw_result['scan']['nmap']['scanstats']

    @property
    def scan(self) -> dict:
        scan = self._raw_result['scan']['scan']
        ips = list(scan.keys())
        return scan[ips.pop()] if len(ips) > 0 else {}

    @property
    def has_tcp(self) -> bool:
        return 'tcp' in self.scan

    @property
    def tcp(self) -> dict:
        return self.scan['tcp'] if self.has_tcp else {}

    @property
    def hostnames(self) -> str:
        result = ''
        scan = self.scan
        if 'hostnames' in scan:
            result = ', '.join(list(map(lambda item: item['name'], scan['hostnames'])))

        return result

    @property
    def host_os(self) -> str:
        result = ''
        scan = self.scan
        if 'osmatch' in scan and len(scan['osmatch']) > 0:
            os = scan['osmatch'][0]
            result = f'{os["name"]} ({os["accuracy"]}%)'

        return result

    @property
    def has_http_service(self) -> bool:
        result = False
        regex = r"http"
        for port_definition in self.tcp.values():
            if re.search(regex, port_definition['name']) is not None:
                result = True
                break

        return result

    def count_ports(self, port_type: str):
        return len(list(filter(lambda item: item['state'] == port_type, self.tcp.values())))

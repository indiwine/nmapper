import re


class ScanResult:
    @staticmethod
    def wrap(results_list: list):
        return list(map(lambda item: ScanResult(item), results_list))

    def __init__(self, raw_result: dict):
        self._raw_result = raw_result

    @property
    def raw_dict(self):
        return self._raw_result

    @property
    def host(self) -> str:
        return self._raw_result['host']

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
        ip = ips.pop()
        return scan[ip]

    @property
    def has_tcp(self) -> bool:
        return 'tcp' in self.scan

    @property
    def tcp(self) -> dict:
        return self.scan['tcp'] if self.has_tcp else {}

    @property
    def has_http_service(self) -> bool:
        result = False
        regex = r"http"
        for port_definition in self.tcp.values():
            if re.search(regex, port_definition['name']) is not None:
                result = True
                break

        return result

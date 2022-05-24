from scanner import ScannerConfig
import nmap
from multiprocessing import Manager


class ScanJob:
    result = None
    scan_result = Manager().dict()

    def __init__(self, config: ScannerConfig, host: str):
        self._config = config
        self._host = host
        self._nm = nmap.PortScannerAsync()

    def scan(self):
        self._nm.scan(self._host, sudo=False, callback=self._callback_result, **self._config.get_nmap_config())

    def get_result(self):
        plain_dict = dict(self.scan_result)
        return plain_dict

    def is_scanning(self):
        return self._nm.still_scanning()

    def _callback_result(self, host, result):
        self.scan_result[host] = result

import logging
from multiprocessing import Manager, Process
import nmap

from scanner import ScannerConfig


def _do_scan(self, host, ports, arguments, sudo, timeout, result_dict):
    scan_data = None
    error = None
    try:
        scan_data = self._nm.scan(host, ports, arguments, sudo, timeout)
        logging.info(f'Scanning of {self.host} have been finished successfully', exc_info=scan_data)
    except Exception as err:
        logging.error(f'Scan of {host} have failed', exc_info=err)
        error = err

    result_dict['scan'] = scan_data
    result_dict['error'] = str(error)


class ScanJob:
    _process = None

    def __init__(self, config: ScannerConfig, host: str):
        logging.debug(f'New job created for host {host}')
        self._config = config
        self.host = host
        self._nm = nmap.PortScanner()
        self.scan_result = Manager().dict()
        self.scan_result['host'] = host
        self.scan_result['success'] = False

    def __del__(self):
        """
        Cleanup when deleted

        """
        if self._process is not None:
            try:
                if self._process.is_alive():
                    self._process.terminate()
            except AssertionError:
                pass

        self._process = None
        return

    def scan(self):
        logging.info(f'Start scanning {self.host}')
        nmap_config = self._config.get_nmap_config()
        self._process = Process(
            target=_do_scan,
            daemon=True,
            args=(self,
                  self.host,
                  nmap_config['ports'],
                  nmap_config['arguments'],
                  False,  # SUDO
                  nmap_config['timeout'], self.scan_result)
        )
        self._process.start()
        logging.debug(f'New process started with pid: {self._process.pid}')

    def get_result(self) -> dict:
        results = dict(self.scan_result)
        results['success'] = results['scan'] is not None
        return results

    def is_scanning(self):
        return self._process.is_alive()

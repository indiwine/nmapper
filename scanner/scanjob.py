import logging

from scanner import ScannerConfig
import nmap
from multiprocessing import Manager, Process


def _do_scan(self, host, ports, arguments, callback, sudo, timeout):
    scan_data = None
    error = None
    try:
        scan_data = self._nm.scan(host, ports, arguments, sudo, timeout)
    except Exception as err:
        error = err

    if callback is not None:
        callback(error, scan_data)


class ScanJob:
    scan_result = Manager().dict()
    _process = None

    def __init__(self, config: ScannerConfig, host: str):
        logging.debug(f'New job created for host {host}')
        self._config = config
        self.host = host
        self._nm = nmap.PortScanner()

    def __del__(self):
        """
        Cleanup when deleted

        """
        if self._process is not None:
            try:
                if self._process.is_alive():
                    self._process.terminate()
            except AssertionError:
                # Happens on python3.4
                # when using PortScannerAsync twice in a row
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
                  self._callback_result,
                  False,  # SUDO
                  nmap_config['timeout'])
        )
        self._process.start()
        logging.debug(f'New process started with pid: {self._process.pid}')

    def get_result(self):
        results = dict(self.scan_result)
        return {
            'host': self.host,
            'success': results['result'] is not None,
            'results': results
        }

    def is_scanning(self):
        return self._process.is_alive()

    def _callback_result(self, error, result):
        if error is not None:
            logging.error(f'Scan of {self.host} have failed', exc_info=error)
        else:
            logging.info(f'Scanning of {self.host} have been finished successfully')

        self.scan_result['scan'] = result
        self.scan_result['error'] = error

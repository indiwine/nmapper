import gc
import logging
from multiprocessing import Manager, Process

import nmap

from scanner.history import ScanSnapshot
from scanner.history.abstractsnapshot import AbstractSnapshot
from scanner.scannerconfig import ScannerConfig


def _do_scan(host, ports, arguments, sudo, timeout, result_dict):
    nm = nmap.PortScanner()

    scan_data = None
    error = None
    try:
        scan_data = nm.scan(host, ports, arguments, sudo, timeout)
        logging.info(f'Scanning of {host} have been finished successfully')
    except Exception as err:
        logging.error(f'Scan of {host} have failed', exc_info=err)
        error = err

    result_dict['scan'] = scan_data
    result_dict['error'] = str(error)


class ScanJob:
    _process: Process = None
    scan_result = {}
    _host = None

    def __init__(self, config: ScannerConfig):
        self._config = config

    @property
    def host(self):
        return self._host

    def set_host(self, host: str):
        self._host = host
        return self

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
        # Initializing state
        self.scan_result = Manager().dict()
        self.scan_result['host'] = self.host
        self.scan_result['success'] = False

        logging.info(f'Start scanning {self.host}')
        nmap_config = self._config.get_nmap_config()
        self._process = Process(
            target=_do_scan,
            daemon=True,
            args=(self.host,
                  nmap_config['ports'],
                  nmap_config['arguments'],
                  False,  # SUDO
                  nmap_config['timeout'],
                  self.scan_result)
        )
        self._process.start()
        logging.debug(f'New process started with pid: {self._process.pid}')

    def get_result(self) -> dict:
        results = dict(self.scan_result)
        results['success'] = self.is_successful
        return results

    def is_scanning(self):
        return self._process.is_alive()

    def save(self) -> AbstractSnapshot:
        logging.debug(f'Saving snapshot scan for host {self._host}')
        return ScanSnapshot(self.get_result())

    def close(self):
        logging.debug(f'Closing process, clearing resources: {self._host}')
        try:
            self.scan_result = None
            self._process.close()
            self._process = None
        except ValueError as e:
            logging.error('Cannot close process, terminating', exc_info=e)
            self._process.terminate()
        gc.collect()

    def restore(self, snapshot: AbstractSnapshot):
        state: dict = snapshot.get_state()
        logging.debug(f'Restoring scan snapshot for host {state["host"]}')
        self._host = state['host']
        self.scan_result = state
        return self

    @property
    def is_successful(self) -> bool:
        return self.scan_result['scan'] is not None

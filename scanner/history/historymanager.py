import logging
import os
import pickle
import shutil
from typing import List

from scanner import ScannerConfig
from scanner.history.abstractsnapshot import AbstractSnapshot


class HistoryManager:
    def __init__(self, pwd: str):
        self._pwd = pwd
        self._history_dir = os.path.join(pwd, '.current_scan')
        self._config_file = os.path.join(self._history_dir, 'scan_config.serial')
        self._snapshot_dir = os.path.join(self._history_dir, 'snapshots')

    def has_unfinished_scan(self) -> bool:
        return os.path.isdir(self._history_dir)

    def clear(self):
        logging.debug(f'Remove current scan dir: {self._history_dir}')
        shutil.rmtree(self._history_dir)

    def create(self):
        logging.debug(f'Creating dir scan dir: {self._history_dir}')
        os.mkdir(self._history_dir)
        logging.debug(f'Creating snapshot dir: {self._snapshot_dir}')
        os.mkdir(self._snapshot_dir)

    def save_config(self, scan_config: ScannerConfig):
        logging.debug(f'Saving config to: {self._config_file}')
        with open(self._config_file, 'wb') as file:
            pickle.dump(scan_config, file)

    def load_config(self) -> ScannerConfig:
        logging.debug(f'Loading config from: {self._config_file}')
        with open(self._config_file, 'rb') as file:
            return pickle.load(file)

    def save_snapshot(self, snapshot: AbstractSnapshot):
        file_name = os.path.join(self._snapshot_dir, snapshot.get_name() + '.serial')
        logging.debug(f'Saving scan snapshot to: {file_name}')
        with open(file_name, 'wb') as file:
            pickle.dump(snapshot, file)

    def load_snapshots(self) -> List[AbstractSnapshot]:
        result = []
        for file in os.listdir(self._snapshot_dir):
            file_path = os.path.join(self._snapshot_dir, file)
            if os.path.isfile(file_path):
                logging.debug(f'Loading scan snapshot from: {file_path}')
                with open(file_path, 'rb') as file_resource:
                    result.append(pickle.load(file_resource))

        return result

import gc
import logging
import time
from typing import List

import click

from scanner import ScanJob
from scanner.history import HistoryManager
from scanner.scannerconfig import ScannerConfig


class ScanManager:
    _active_jobs: List[ScanJob] = []
    _next_index = 0

    def __init__(self, config: ScannerConfig, history_manager: HistoryManager):
        self._config = config
        self._history_manager = history_manager
        self._hosts_to_scan = config.scanner_hosts.parsedHosts
        self._parallel_num = config.get_parallel_num()
        self._num_hosts_to_scan = len(self._hosts_to_scan)

    def continue_scan(self) -> None:
        logging.info('Continuing previous scan')

        hosts_omitted = 0
        for snapshot in self._history_manager.load_snapshots_generator():
            job = ScanJob(self._config)
            job.restore(snapshot)
            if job.host in self._hosts_to_scan:
                hosts_omitted += 1
                self._hosts_to_scan.remove(job.host)

        self._num_hosts_to_scan = len(self._hosts_to_scan)

        click.echo(click.style(f'Omitted {hosts_omitted} host(s). Using data from previous scan.',
                               fg='green'))

        self.scan()

    def scan(self) -> None:
        click.echo(click.style(f'Start scanning {self._num_hosts_to_scan} host(s), {self._parallel_num} in parallel',
                               fg='green'))

        # Pre-filling active jobs list
        self._check_active_jobs()

        with click.progressbar(
                length=len(self._hosts_to_scan),
                show_eta=True,
                show_pos=True,
        ) as bar:
            while True:
                done_num = self._check_active_jobs()
                if self._has_no_hosts_left():
                    logging.info('No more hosts to scan left')
                    break
                bar.update(done_num)
                time.sleep(0.05)

        click.echo(click.style(f'Scanning of {self._num_hosts_to_scan} hosts have been finished.',
                               fg='green'))

    def _has_no_hosts_left(self) -> bool:
        return len(self._active_jobs) == 0 and (self._next_index + 1) > self._num_hosts_to_scan

    def _get_next_job(self):
        if (self._next_index + 1) > self._num_hosts_to_scan:
            return None

        host = self._hosts_to_scan[self._next_index]
        self._next_index += 1
        return ScanJob(self._config).set_host(host)

    def _check_active_jobs(self) -> int:
        done_num = 0
        for job in self._active_jobs:
            if not job.is_scanning():
                self._active_jobs.remove(job)
                self._history_manager.save_snapshot(job.save())
                job.close()
                done_num += 1

        while len(self._active_jobs) < self._parallel_num:
            next_job = self._get_next_job()
            if next_job is None:
                break
            next_job.scan()
            self._active_jobs.append(next_job)

        if done_num > 0:
            gc.collect()

        return done_num

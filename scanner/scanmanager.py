import logging
import time

import click

from scanner import ScannerConfig, ScanJob


class ScanManager:
    _active_jobs = []
    _done_jobs = []
    _next_index = 0

    def __init__(self, config: ScannerConfig):
        self._config = config
        self._hosts_to_scan = config.scanner_hosts.parsedHosts
        self._parallel_num = config.get_parallel_num()
        self._num_hosts_to_scan = len(self._hosts_to_scan)

    def scan(self):
        click.echo(click.style(f'Start scanning {self._num_hosts_to_scan} host(s), {self._parallel_num} in parallel',
                               fg='green'))

        # Pre-filling active jobs list
        self._check_active_jobs()

        with click.progressbar(
                length=len(self._hosts_to_scan),
                show_eta=True,
                show_pos=True,
                item_show_func=self._format_active_scans
        ) as bar:
            while True:
                done_num = self._check_active_jobs()
                if self._has_no_hosts_left():
                    logging.info('No more hosts to scan left')
                    break
                time.sleep(0.05)
                bar.update(done_num)

        failed = 0
        success = 0
        scanned_hosts = []
        for job in self._done_jobs:
            results = job.get_result()
            scanned_hosts.append(results)
            if results['success']:
                success += 1
            else:
                failed += 1

        click.echo(click.style(f'Scanning of {self._num_hosts_to_scan} hosts have been finished. '
                               f'Of them: {success} succeeded, {failed} failed.',
                               fg='green'))

        return scanned_hosts

    def _has_no_hosts_left(self):
        return len(self._active_jobs) == 0 and (self._next_index + 1) > self._num_hosts_to_scan

    def _get_next_job(self):
        if (self._next_index + 1) > self._num_hosts_to_scan:
            return None

        host = self._hosts_to_scan[self._next_index]
        self._next_index += 1
        return ScanJob(self._config, host)

    def _format_active_scans(self, s):
        return 'Now: ' + '|'.join(map(lambda job: job.host, self._active_jobs))

    def _check_active_jobs(self):
        done_num = 0
        for job in self._active_jobs:
            if not job.is_scanning():
                self._active_jobs.remove(job)
                self._done_jobs.append(job)
                done_num += 1

        while len(self._active_jobs) < self._parallel_num:
            next_job = self._get_next_job()
            if next_job is None:
                break
            next_job.scan()
            self._active_jobs.append(next_job)
        return done_num

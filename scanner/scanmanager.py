import time

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
        while True:
            self._check_active_jobs()
            if self._has_no_hosts_left():
                break
            time.sleep(0.05)

        result = []
        for job in self._done_jobs:
            results = job.get_result()
            result.append(results)

        return result

    def _has_no_hosts_left(self):
        return len(self._active_jobs) == 0 and (self._next_index + 1) > self._num_hosts_to_scan

    def _get_next_job(self):
        if (self._next_index + 1) > self._num_hosts_to_scan:
            return None

        host = self._hosts_to_scan[self._next_index]
        self._next_index += 1
        return ScanJob(self._config, host)

    def _check_active_jobs(self):
        for job in self._active_jobs:
            if not job.is_scanning():
                self._active_jobs.remove(job)
                self._done_jobs.append(job)

        while len(self._active_jobs) < self._parallel_num:
            next_job = self._get_next_job()
            if next_job is None:
                break
            next_job.scan()
            self._active_jobs.append(next_job)

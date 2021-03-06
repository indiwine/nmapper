import ipaddress
import logging
from typing import List

import click
import yaml
from fqdn import FQDN


class ScannerHosts:
    parsedHosts: List[str] = []

    def __init__(self, hosts: list):
        self._rawHosts = hosts
        self._parse_raw_hosts()

    def __getstate__(self):
        return self.parsedHosts

    def __setstate__(self, state):
        self.parsedHosts = state

    def _parse_raw_hosts(self):
        for host in self._rawHosts:
            # Checking if it's a hostname
            hostname = FQDN(host)
            if hostname.is_valid:
                self.parsedHosts.append(host)
                logging.debug(f'Hostname detected: {host}')
                continue

            ip_interface = ipaddress.ip_interface(host)
            for ip in ip_interface.network.hosts():
                self.parsedHosts.append(str(ip))

        click.echo(click.style(f'Calculated {len(self.parsedHosts)} host(s) to scan', fg='green'))


class ScannerConfig:
    _rawYaml: dict = None

    scanner_hosts: ScannerHosts = None

    def load_from_yaml(self, path: str):
        logging.debug('Reading config file %s', path)
        stream = open(path, 'r')
        self._rawYaml = yaml.full_load(stream)
        logging.debug('Config file loaded')
        self.scanner_hosts = ScannerHosts(self._rawYaml['scanner']['hosts'])

    def get_nmap_config(self):
        nmap_config = self._rawYaml['nmap']
        nmap_timeout = 0
        if nmap_config['timeout'] is not None:
            nmap_timeout = nmap_config['timeout']

        return {
            'ports': nmap_config['ports'],
            'arguments': nmap_config['arguments'],
            'timeout': nmap_timeout
        }

    def get_parallel_num(self) -> int:
        parallel = 1
        if self._rawYaml['scanner']['parallel']:
            parallel = self._rawYaml['scanner']['parallel']

        return parallel

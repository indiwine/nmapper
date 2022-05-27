import gc
import json
import os

import click
import logging

from formatter import FormatterManager
from scanner import ScannerConfig, ScanManager, ScanResult


@click.command()
@click.option('-v', '--verbose', count=True)
@click.option('-c', '--config', default='./config.yaml', show_default=True, help='Config file used for scan')
def run_scan(verbose, config):
    log_level = logging.ERROR
    if verbose == 1:
        log_level = logging.WARNING
    elif verbose == 2:
        log_level = logging.INFO
    elif verbose == 3:
        log_level = logging.DEBUG
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    scanner_config = ScannerConfig(os.path.join(os.getcwd(), config))
    manager = ScanManager(scanner_config)
    scan_results = manager.scan()
    del manager
    gc.collect()

    scan_results = ScanResult.wrap(scan_results)

    formatter = FormatterManager(scan_results)
    formatter.save_json_results()
    formatter.output()


if __name__ == '__main__':
    run_scan()

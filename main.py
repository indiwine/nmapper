import gc
import logging
import os

import click

from formatter import FormatterManager
from scanner import ScanManager, ScanResult
from scanner.scannerconfig import ScannerConfig
from scanner.history import HistoryManager


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

    history = HistoryManager(os.getcwd())
    continue_scan = False
    if history.has_unfinished_scan():
        continue_scan = click.prompt('There is an unfinished scan found, continue?', default=True)
        if not continue_scan:
            # Clearing previous scan
            history.clear()

    if continue_scan:
        scanner_config = history.load_config()
    else:
        scanner_config = ScannerConfig()

        history.create()
        scanner_config.load_from_yaml(os.path.join(os.getcwd(), config))
        history.save_config(scanner_config)

    manager = ScanManager(scanner_config, history)

    if continue_scan:
        scan_results = manager.continue_scan()
    else:
        scan_results = manager.scan()

    del manager
    gc.collect()

    scan_results = ScanResult.wrap(scan_results)

    formatter = FormatterManager(scan_results)
    formatter.save_json_results()
    formatter.output()
    history.clear()


if __name__ == '__main__':
    run_scan()

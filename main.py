import os

import click
import logging
import click_log

from scanner import ScannerConfig, ScanManager

logger = logging.getLogger('nmapper')
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
# click_log.basic_config(logger)


@click.command()
@click_log.simple_verbosity_option(logger)
def run_scan():
    config = ScannerConfig(f'{os.getcwd()}/config.example.yaml')

    manager = ScanManager(config)
    scan_results = manager.scan()


if __name__ == '__main__':
    run_scan()

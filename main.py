import gc
import json
import os

import click
import logging
import click_log

from formatter import FormatterManager
from scanner import ScannerConfig, ScanManager, ScanResult

logger = logging.getLogger('nmapper')
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
# click_log.basic_config(logger)


@click.command()
@click_log.simple_verbosity_option(logger)
def run_scan():
    # config = ScannerConfig(f'{os.getcwd()}/config.example.yaml')
    # manager = ScanManager(config)
    # scan_results = manager.scan()
    # del manager
    # gc.collect()

    raw_results = open('scan-26-05-2022-112143/raw_results.json', 'r')
    scan_results = json.load(raw_results)

    scan_results = ScanResult.wrap(scan_results)

    formatter = FormatterManager(scan_results)
    formatter.output()
    # formatter.save_json_results()



if __name__ == '__main__':
    run_scan()

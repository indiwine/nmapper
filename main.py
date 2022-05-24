import click
import logging
import click_log

from scanner import ScannerConfig, ScanManager

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


@click.command()
@click_log.simple_verbosity_option(logger)
def hello():
    config = ScannerConfig('config.example.yaml')
    manager = ScanManager(config)
    scan_results = manager.scan()
    print(scan_results)


if __name__ == '__main__':
    hello()

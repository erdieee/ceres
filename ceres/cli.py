import argparse
import logging
import time
import sys
from typing import List, Optional

from ceres import __version__
from ceres.ceresbot import CeresBot
from ceres.utils import load_config

logger = logging.getLogger(__name__)


def trade(args):
    """Start trading"""
    LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=20, format=LOGFORMAT)
    config = load_config()
    logger.info("Starting ceres")
    ceresbot = CeresBot(config)
    heart_beat_now = 0
    heart_beat = 60
    while True:
        now = time.time()
        if (now - heart_beat_now) > heart_beat:
            logger.info(f"Bot heartbeat. Running version='{__version__}'")
            heart_beat_now = now
        ceresbot.main_loop()


def new_config(args):
    raise NotImplementedError(f"Use the config template on github for now.")


def parse_arguments(sysargv):
    try:
        parser = argparse.ArgumentParser(
            prog="ceres", description="Crypto Arbitrage bot"
        )
        parser.add_argument("-v", "--verbose", help="Verbose mode")
        parser.add_argument(
            "-V",
            "--version",
            help="Show bots version",
            action="version",
            version=f"Version: {__version__}",
        )
        subparsers = parser.add_subparsers()

        trade_command = subparsers.add_parser("trade", help="Start trading.")
        trade_command.set_defaults(func=trade)

        config_command = subparsers.add_parser(
            "create-config", help="Create a new config."
        )
        config_command.set_defaults(func=new_config)
        config_command.add_argument(
            "--name", help="Specify the name of the config you want to create."
        )

        args = parser.parse_args(sysargv)
        return args
    except argparse.ArgumentError as e:
        logger.error(e)


def cli(sysargv: Optional[List] = None):
    args = parse_arguments(sysargv)
    # print(args)
    if "func" in args:  # type: ignore
        args.func(args)  # type: ignore
    else:
        print("No command specified. Use 'ceres --help' to view all commands.")
        sys.exit()


if __name__ == "__main__":
    cli()

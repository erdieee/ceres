import logging
import time

import typer

from ceres import __version__
from ceres.ceresbot import CeresBot
from ceres.utils import load_config

cli = typer.Typer(help="Ceres bot cli", add_completion=False)


@cli.command()
def trade(
    verbose: int = typer.Option(logging.INFO, "-v", "--verbose", help="Verbose mode")
):
    """Start trading"""
    logger = logging.getLogger("ceres")
    LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=verbose, format=LOGFORMAT)
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


@cli.command()
def show_trades():
    """Show last trades"""
    raise NotImplementedError()


@cli.command(help="Bot version")
def version():
    """Display the current version of the bot"""
    print(f"Ceres version: {__version__}")


if __name__ == "__main__":
    cli()

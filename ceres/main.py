#!/usr/bin/env python3

import logging
import time

from ceres import __version__
from ceres.ceresbot import CeresBot
from ceres.utils import load_config


logger = logging.getLogger("ceres")
LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOGFORMAT)


def main() -> None:
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

if __name__ == "__main__":
    main()

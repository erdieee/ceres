#!/usr/bin/env python3
import logging
import sys

from rich.logging import RichHandler

from ceres.cli import cli

logger = logging.getLogger("ceres")
LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# logging.basicConfig(level=20, format=LOGFORMAT, handlers=[RichHandler())
logging.basicConfig(
    level=20,
    format=LOGFORMAT,
    datefmt="[%X]",
    handlers=[logging.FileHandler("logs.log")],
)


def main() -> None:
    try:
        cli()
    except KeyboardInterrupt:
        logger.info("SIGINT received, aborting ...")
    except Exception:
        logger.exception("Exception")
    finally:
        sys.exit()


if __name__ == "__main__":
    main()

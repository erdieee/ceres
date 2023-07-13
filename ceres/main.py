#!/usr/bin/env python3
import logging
import sys

from ceres.cli import cli

logger = logging.getLogger("ceres")


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

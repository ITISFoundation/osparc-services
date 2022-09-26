#!/usr/bin/python

""" Tries to pull the node data from S3. Will return error code unless the --silent flag is on and only a warning will be output.

    Usage python state_puller.py PATH_OR_FILE --silent
:return: error code
"""

import argparse
import asyncio
import logging
import sys
from enum import IntEnum
from pathlib import Path

from simcore_sdk.node_data import data_manager

log = logging.getLogger(__file__ if __name__ == "__main__" else __name__)
logging.basicConfig(level=logging.INFO)


class ExitCode(IntEnum):
    SUCCESS = 0
    FAIL = 1


async def pull_file_if_exists(path: Path) -> None:
    """
    If the path already exist in storage pull it. Otherwise it is assumed
    this is the first time the service starts.

    In each and every other case an error is raised and logged
    """
    if not await data_manager.is_file_present_in_storage(path):
        log.info("File '%s' is not present in storage service, will skip.", str(path))
        return

    await data_manager.pull(path)
    log.info("Finished pulling and extracting %s", str(path))


def main(args=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path", help="The folder or file to get for the node", type=Path
    )
    options = parser.parse_args(args)
    try:
        asyncio.get_event_loop().run_until_complete(
            pull_file_if_exists(path=options.path)
        )
    except Exception:  # pylint: disable=broad-except
        log.exception(
            "Unexpected error when retrieving state from S3 for %s", options.path
        )
        return ExitCode.FAIL
    return ExitCode.SUCCESS


if __name__ == "__main__":
    sys.exit(main())

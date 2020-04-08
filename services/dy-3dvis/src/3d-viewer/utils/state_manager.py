#!/usr/bin/python

""" Tries to pull the node data from S3. Will return error code unless the --silent flag is on and only a warning will be output.

    Usage python state_puller.py PATH_OR_FILE --silent
:return: error code
"""

import argparse
import asyncio
import logging
import os
import sys
import time
from enum import IntEnum
from pathlib import Path

from simcore_sdk.node_data import data_manager
from simcore_sdk.node_ports import exceptions

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__ if __name__ == "__main__" else __name__)


class ExitCode(IntEnum):
    SUCCESS = 0
    FAIL = 1


def state_path() -> Path:
    path = os.environ.get("SIMCORE_NODE_APP_STATE_PATH", "undefined")
    assert path != "undefined", "SIMCORE_NODE_APP_STATE_PATH is not defined!"
    return Path(path)


def main(args=None) -> int:
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--path", help="The folder or file to get for the node",
                            type=Path, default=state_path(), required=False)
        parser.add_argument("--silent", help="The script will silently fail if the flag is on",
                            default=False, const=True, action="store_const", required=False)
        parser.add_argument("type", help="push or pull",
                            choices=["push", "pull"])
        options = parser.parse_args(args)

        loop = asyncio.get_event_loop()

        # push or pull state
        start_time = time.clock()
        loop.run_until_complete(getattr(data_manager, options.type)(options.path))
        end_time = time.clock()
        log.info("time to %s: %.2fseconds", options.type, end_time - start_time)
        return ExitCode.SUCCESS

    except exceptions.S3InvalidPathError:
        if options.silent:
            log.warning("Could not %s state from S3 for %s", options.type, options.path)
            return ExitCode.SUCCESS
        log.exception("Could not %s state from S3 for %s", options.type, options.path)
        return ExitCode.FAIL
    except:  # pylint: disable=bare-except
        log.exception("Unexpected error when %s state from/to S3 for %s", options.type, options.path)
        return ExitCode.FAIL


if __name__ == "__main__":
    sys.exit(main())

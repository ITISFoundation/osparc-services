#!/usr/bin/python

""" Tries to pull the node data from S3. Will return error code.

    Usage python state_puller.py PATH_OR_FILE
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

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__ if __name__ == "__main__" else __name__)


class ExitCode(IntEnum):
    SUCCESS = 0
    FAIL = 1


def state_path() -> Path:
    path = os.environ.get("SIMCORE_NODE_APP_STATE_PATH", "undefined")
    assert path != "undefined", "SIMCORE_NODE_APP_STATE_PATH is not defined!"
    return Path(path)

async def push_pull_state(path, op_type) -> None:
    if op_type == "pull":
        if not await data_manager.is_file_present_in_storage(path):
            log.info("File '%s' is not present in storage service, will skip.", str(path))
            return
    await getattr(data_manager, op_type)(path)

def main(args=None) -> int:
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--path", help="The folder or file to get for the node",
                            type=Path, default=state_path(), required=False)
        parser.add_argument("type", help="push or pull",
                            choices=["push", "pull"])
        options = parser.parse_args(args)

        loop = asyncio.get_event_loop()

        # push or pull state
        start_time = time.clock()
        loop.run_until_complete(push_pull_state(options.path, options.type))
        end_time = time.clock()
        log.info("time to %s: %.2fseconds", options.type, end_time - start_time)
        return ExitCode.SUCCESS

    except Exception: # pylint: disable=broad-except
        log.exception("Could not %s state from S3 for %s", options.type, options.path)
        return ExitCode.FAIL


if __name__ == "__main__":
    sys.exit(main())

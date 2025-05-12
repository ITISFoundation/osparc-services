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
    return

def main(args=None) -> int:
    return ExitCode.SUCCESS

if __name__ == "__main__":
    sys.exit(main())

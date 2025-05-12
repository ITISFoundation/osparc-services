#!/usr/bin/python

import argparse
import asyncio
import json
import logging
import os
import shutil
import sys
import tempfile
import time
import zipfile
from enum import IntEnum
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__ if __name__ == "__main__" else __name__)

CACHE_FILE_PATH = Path(tempfile.gettempdir()) / "input_retriever.cache"


class ExitCode(IntEnum):
    SUCCESS = 0
    FAIL = 1


def input_path() -> Path:
    path = os.environ.get("PARAVIEW_INPUT_PATH", "undefined")
    assert path != "undefined", "PARAVIEW_INPUT_PATH is not defined!"
    return Path(path)


async def task(node_key: str, fct, *args, **kwargs):
    return (node_key, await fct(*args, *kwargs))


async def retrieve_data(ports: List[str], cache: Dict) -> int:
    return 0


def main(args=None) -> int:
    return ExitCode.SUCCESS

if __name__ == "__main__":
    sys.exit(main())

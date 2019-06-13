#!/usr/bin/python

import argparse
import asyncio
import logging
import os
import shutil
import sys
import time
import zipfile
from enum import IntEnum
from pathlib import Path

from simcore_sdk import node_ports

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__ if __name__ == "__main__" else __name__)


class ExitCode(IntEnum):
    SUCCESS = 0
    FAIL = 1


def input_path() -> Path:
    path = os.environ.get("PARAVIEW_INPUT_PATH", "undefined")
    assert path != "undefined", "PARAVIEW_INPUT_PATH is not defined!"
    return Path(path)


async def retrieve_data():
    # get all files in the local system and copy them to the input folder
    start_time = time.clock()
    PORTS = node_ports.ports()
    download_tasks = []
    for node_input in PORTS.inputs:
        if not node_input or node_input.value is None:
            continue
        # collect coroutines
        download_tasks.append(node_input.get())
    log.info("retrieving %s data", len(download_tasks))

    if download_tasks:
        downloaded_files = await asyncio.gather(*download_tasks)
        log.info("completed download, extracting/moving data to final folder...")
        for local_path in downloaded_files:
            if local_path is None:
                continue

            if not local_path.exists():
                continue

            if zipfile.is_zipfile(str(local_path)):
                log.info("extracting %s to %s", local_path, input_path())
                zip_ref = zipfile.ZipFile(str(local_path), 'r')
                zip_ref.extractall(str(input_path()))
                zip_ref.close()
                log.info("extraction completed")
            else:
                log.info("moving %s to input path %s",
                         local_path, input_path())
                shutil.move(str(local_path), str(
                    input_path() / local_path.name))
                log.info("move completed")
        end_time = time.clock()
        log.info("retrieval complete: took %.2fseconds", end_time - start_time)


def main(args=None) -> int:
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.parse_args(args)

        if not input_path().exists():
            input_path().mkdir()
            log.info("Created input folder at %s", input_path())

        loop = asyncio.get_event_loop()
        loop.run_until_complete(retrieve_data())
        return ExitCode.SUCCESS
    except:  # pylint: disable=bare-except
        log.exception("Unexpected error when retrievin data")
        return ExitCode.FAIL


if __name__ == "__main__":
    sys.exit(main())

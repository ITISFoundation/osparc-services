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

from simcore_sdk import node_ports

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
    # get all files in the local system and copy them to the input folder
    start_time = time.clock()
    PORTS = node_ports.ports()
    download_tasks = []
    for node_input in PORTS.inputs:
        # if ports contains some keys only download them
        log.info("Checking node %s", node_input.key)
        if ports and node_input.key not in ports:
            continue
        # delete the corresponding file(s) if applicable
        if node_input.key in cache:
            log.info("Deleting files from %s: %s", node_input.key, cache[node_input.key])
            for file_path in cache[node_input.key]:
                Path(file_path).unlink()
            del cache[node_input.key]
        if not node_input or node_input.value is None:            
            continue
        # collect coroutines
        download_tasks.append(task(node_input.key, node_input.get))
    log.info("retrieving %s data", len(download_tasks))

    if download_tasks:
        download_results = await asyncio.gather(*download_tasks)
        log.info("completed download, extracting/moving data to final folder...")
        for node_key, local_path in download_results:
            if local_path is None:
                continue

            if not local_path.exists():
                continue

            if zipfile.is_zipfile(str(local_path)):
                log.info("extracting %s to %s", local_path, input_path())
                zip_ref = zipfile.ZipFile(str(local_path), 'r')
                zip_ref.extractall(str(input_path()))
                cache[node_key] = \
                    [str(input_path() / zipped_file) for zipped_file in zip_ref.namelist()] 
                zip_ref.close()
                log.info("extraction completed")
            else:
                log.info("moving %s to input path %s",
                         local_path, input_path())
                dest_path = input_path() / local_path.name
                shutil.move(str(local_path), str(dest_path))
                cache[node_key] = [str(dest_path)]
                log.info("move completed")
        end_time = time.clock()
        log.info("retrieval complete: took %.2fseconds", end_time - start_time)


def main(args=None) -> int:
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--port_keys", help="The port keys to push/pull",
                            type=str, nargs="*", required=True)
        options = parser.parse_args(args)
        log.info("has to retrieve the following ports: %s", 
                                    options.port_keys if options.port_keys else "all"
                                    )

        if not input_path().exists():
            input_path().mkdir()
            log.info("Created input folder at %s", input_path())

        file_transfer_history = {}
        if CACHE_FILE_PATH.exists():
            with CACHE_FILE_PATH.open() as fp:
                file_transfer_history = json.load(fp)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(retrieve_data(options.port_keys, file_transfer_history))
        log.info("saving cache: %s", file_transfer_history)
        with CACHE_FILE_PATH.open("w") as fp:
            json.dump(file_transfer_history, fp)

        return ExitCode.SUCCESS
    except:  # pylint: disable=bare-except
        log.exception("Unexpected error when retrievin data")
        return ExitCode.FAIL


if __name__ == "__main__":
    sys.exit(main())

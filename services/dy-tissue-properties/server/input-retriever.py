import asyncio
import logging
import os
import sys
from pathlib import Path

from simcore_sdk import node_ports

logger = logging.getLogger(__name__)

_OUTPUTS_FOLDER = Path(os.environ.get("TISSUEPROPS_OUTPUT_PATH"))


if not _OUTPUTS_FOLDER.exists():
    _OUTPUTS_FOLDER.mkdir()
    logger.debug("Created output folder at %s", _OUTPUTS_FOLDER)


async def upload_data():
    logger.info("uploading data to simcore...")
    PORTS = node_ports.ports()
    outputs_path = Path(_OUTPUTS_FOLDER).expanduser()
    for port in PORTS.outputs:
        logger.debug("uploading data to port '%s' with value '%s'...", port.key, port.value)
        src_folder = outputs_path / port.key
        list_files = list(src_folder.glob("*"))
        if len(list_files) == 1:
            # special case, direct upload
            await port.set(list_files[0])
            continue

    logger.info("all data uploaded to simcore")

async def sync_data():
    try:
        await upload_data()
    except node_ports.exceptions.NodeportsException as exc:
        logger.error("error when syncing '%s'", str(exc))
        sys.exit(1)
    finally:
        logger.info("download and upload finished")

asyncio.get_event_loop().run_until_complete(sync_data())

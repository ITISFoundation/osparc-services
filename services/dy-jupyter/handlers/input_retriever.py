import asyncio
import json
import logging
import os
import shutil
import tempfile
import time
import zipfile
from typing import List
from pathlib import Path

from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join
from simcore_sdk import node_ports
# from simcore_sdk.node_ports import filemanager
# from simcore_sdk.node_ports import log as node_logger

logger = logging.getLogger(__name__)
# node_logger.setLevel(logging.DEBUG)
# filemanager.CHUNK_SIZE = 16*1024*1024


_INPUTS_FOLDER =  os.environ.get("INPUTS_FOLDER", "~/inputs")
_OUTPUTS_FOLDER = os.environ.get("OUTPUTS_FOLDER", "~/outputs")
_FILE_TYPE_PREFIX = "data:"
_KEY_VALUE_FILE_NAME = "key_values.json"

def _compress_files_in_folder(folder: Path, one_file_not_compress: bool = True) -> Path:
    list_files = list(folder.glob("*"))

    if list_files is None:
        return None

    if one_file_not_compress and len(list_files) == 1:
        return list_files[0]

    temp_file = tempfile.NamedTemporaryFile(suffix=".zip")
    temp_file.close()
    with zipfile.ZipFile(temp_file.name, mode="w") as zip_ptr:
        for file_path in list_files:
            zip_ptr.write(str(file_path), arcname=file_path.name)
        
    return Path(temp_file.name)

def _no_relative_path_zip(members: zipfile.ZipFile):
    for zipinfo in members.infolist():
        path = Path(zipinfo.filename)
        if path.is_absolute():
            # absolute path are not allowed
            continue
        if path.match("/../"):
            # relative paths are not allowed
            continue
        yield zipinfo.filename

async def get_time_wrapped(port):
    logger.info("transfer started for %s", port.key)
    start_time = time.perf_counter()
    ret = await port.get()
    elapsed_time = time.perf_counter() - start_time
    logger.info("transfer completed in %ss", elapsed_time)
    if isinstance(ret, Path):
        size_mb = ret.stat().st_size / 1024 / 1024
        logger.info("%s: data size: %sMB, transfer rate %sMB/s", ret.name, size_mb, size_mb / elapsed_time)    
    return (port, ret)

async def set_time_wrapped(port, value):
    logger.info("transfer started for %s", port.key)
    start_time = time.perf_counter()
    await port.set(value)
    elapsed_time = time.perf_counter() - start_time
    logger.info("transfer completed in %ss", elapsed_time)
    if isinstance(value, Path):
        size_mb = value.stat().st_size / 1024 / 1024
        logger.info("%s: data size: %sMB, transfer rate %sMB/s", value.name, size_mb, size_mb / elapsed_time)    
    

async def download_data(port_keys: List[str]) -> int:
    logger.info("retrieving data from simcore...")
    start_time = time.perf_counter()
    PORTS = node_ports.ports()
    inputs_path = Path(_INPUTS_FOLDER).expanduser()
    data = {}

    # let's gather all the data
    download_tasks = []
    for node_input in PORTS.inputs:
        # if port_keys contains some keys only download them
        logger.info("Checking node %s", node_input.key)
        if port_keys and node_input.key not in port_keys:
            continue
        if not node_input or node_input.value is None:            
            continue
        # collect coroutines
        download_tasks.append(get_time_wrapped(node_input))
    logger.info("retrieving %s data", len(download_tasks))    
    
    
    transfer_bytes = 0
    if download_tasks:
        results = await asyncio.gather(*download_tasks)
        logger.info("completed download %s", results)
        for port, value in results:
            data[port.key] = {"key": port.key, "value": value}
            
            if _FILE_TYPE_PREFIX in port.type:
                # if there are files, move them to the final destination
                downloaded_file = value
                dest_path = inputs_path / port.key
                # first cleanup
                logger.info("removing %s", dest_path)
                shutil.rmtree(dest_path)
                if not downloaded_file or not downloaded_file.exists():
                    # the link may be empty
                    continue
                transfer_bytes = transfer_bytes + downloaded_file.stat().st_size
                # in case of valid file, it is either uncompressed and/or moved to the final directory
                logger.info("creating directory %s", dest_path)
                dest_path.mkdir(exist_ok=True, parents=True)
                data[port.key] = {"key": port.key, "value": str(dest_path)}

                if zipfile.is_zipfile(downloaded_file):
                    logger.info("unzipping %s", downloaded_file)
                    with zipfile.ZipFile(downloaded_file) as zip_file:
                        zip_file.extractall(dest_path, members=_no_relative_path_zip(zip_file))
                    logger.info("all unzipped in %s", dest_path)
                else:
                    logger.info("moving %s", downloaded_file)
                    dest_path = dest_path / Path(downloaded_file).name
                    shutil.move(downloaded_file, dest_path)
                    logger.info("all moved to %s", dest_path)
            else:
                transfer_bytes = transfer_bytes + sys.getsizeof(value)
    # if data other than file, copy them to a json file
    data_file = inputs_path / _KEY_VALUE_FILE_NAME
    data_file.write_text(json.dumps(data))
    stop_time = time.perf_counter()
    logger.info("all data retrieved from simcore in %sseconds: %s", stop_time - start_time, data)
    return transfer_bytes

async def upload_data(port_keys: List[str]) -> int:
    logger.info("uploading data to simcore...")
    start_time = time.perf_counter()
    PORTS = node_ports.ports()
    outputs_path = Path(_OUTPUTS_FOLDER).expanduser()
    upload_tasks = []
    temp_files = []
    transfer_bytes = 0
    for port in PORTS.outputs:
        logger.debug("uploading data to port '%s' with value '%s'...", port.key, port.value)
        if _FILE_TYPE_PREFIX in port.type:
            src_folder = outputs_path / port.key
            list_files = list(src_folder.glob("*"))
            if len(list_files) == 1:
                # special case, direct upload
                upload_tasks.append(set_time_wrapped(port, list_files[0]))
                continue
            # generic case let's create an archive
            if len(list_files) > 1:
                temp_file = tempfile.NamedTemporaryFile(suffix=".zip")
                temp_file.close()
                with zipfile.ZipFile(temp_file.name, mode="w") as zip_ptr:
                    for file_path in list_files:
                        zip_ptr.write(str(file_path), arcname=file_path.name)
                
                temp_files.append(temp_file.name)
                upload_tasks.append(set_time_wrapped(port, temp_file.name))
        else:
            data_file = outputs_path / _KEY_VALUE_FILE_NAME
            if data_file.exists():
                data = json.loads(data_file.read_text())
                if port.key in data and data[port.key] is not None:
                    upload_tasks.append(set_time_wrapped(port, data[port.key]))

        try:
            await asyncio.gather(*upload_tasks)
        finally:
            # clean up possible compressed files
            for file_path in temp_files:
                Path(file_path).unlink()
    stop_time = time.perf_counter()
    logger.info("all data uploaded to simcore in %sseconds", stop_time-start_time)
    return transfer_bytes


class RetrieveHandler(IPythonHandler):
    def initialize(self): #pylint: disable=no-self-use
        PORTS = node_ports.ports()
        _create_ports_sub_folders(PORTS.inputs, Path(_INPUTS_FOLDER).expanduser())
        _create_ports_sub_folders(PORTS.outputs, Path(_OUTPUTS_FOLDER).expanduser())
        self.file_transfer_history = {}

    async def get(self):
        try:
            results = await asyncio.gather(download_data(port_keys=[]), upload_data(port_keys=[]))
            transfered_size = sum(results)
            self.write(json.dumps({
                "data": {
                    "size_bytes": transfered_size
                }
            }))
            self.set_status(200)
        except node_ports.exceptions.NodeportsException as exc:
            logger.exception("Unexpected problem when processing retrieve call")
            self.set_status(500, reason=str(exc))
        except Exception as exc: #pylint: disable=broad-except
            logger.exception("Unexpected problem when processing retrieve call")
            self.set_status(500, reason=str(exc))
        finally:
            self.finish('completed retrieve!')
    
    async def post(self):
        request_contents = json.loads(self.request.body)
        ports = request_contents["port_keys"]
        logger.info("getting data of ports %s from previous node with POST request...", ports)
        try:
            results = await asyncio.gather(download_data(ports), upload_data(ports))
            transfered_size = sum(results)
            self.write(json.dumps({
                "data": {
                    "size_bytes": transfered_size
                }
            }))
            self.set_status(200)
        except node_ports.exceptions.NodeportsException as exc:
            logger.exception("Unexpected problem when processing retrieve call")
            self.set_status(500, reason=str(exc))
        except Exception as exc: #pylint: disable=broad-except
            logger.exception("Unexpected problem when processing retrieve call")
            self.set_status(500, reason=str(exc))
        finally:
            self.finish()


def _create_ports_sub_folders(ports: node_ports._items_list.ItemsList, parent_path: Path): # pylint: disable=protected-access
    values = {}
    for port in ports:
        values[port.key] = port.value
        if _FILE_TYPE_PREFIX in port.type:
            sub_folder = parent_path / port.key
            sub_folder.mkdir(exist_ok=True, parents=True)

    parent_path.mkdir(exist_ok=True, parents=True)
    values_file = parent_path / _KEY_VALUE_FILE_NAME
    values_file.write_text(json.dumps(values))

def _init_sub_folders():
    Path(_INPUTS_FOLDER).expanduser().mkdir(exist_ok=True, parents=True)
    Path(_OUTPUTS_FOLDER).expanduser().mkdir(exist_ok=True, parents=True)



def load_jupyter_server_extension(nb_server_app):
    """ Called when the extension is loaded

    - Adds API to server

    :param nb_server_app: handle to the Notebook webserver instance.
    :type nb_server_app: NotebookWebApplication
    """
    _init_sub_folders()

    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/retrieve')

    web_app.add_handlers(host_pattern, [(route_pattern, RetrieveHandler)])

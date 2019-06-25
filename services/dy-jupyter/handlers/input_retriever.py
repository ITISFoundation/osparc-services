import asyncio
import json
import logging
import os
import shutil
import tarfile
import tempfile
import time
import zipfile
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

    temp_file = tempfile.NamedTemporaryFile(suffix=".tgz")
    temp_file.close()
    for _file in list_files:
        with tarfile.open(temp_file.name, mode='w:gz') as tar_ptr:
            for file_path in list_files:
                tar_ptr.add(str(file_path), arcname=file_path.name, recursive=False)
    return Path(temp_file.name)

def _no_relative_path_tar(members: tarfile.TarFile):
    for tarinfo in members:
        path = Path(tarinfo.name)
        if path.is_absolute():
            # absolute path are not allowed
            continue
        if path.match("/../"):
            # relative paths are not allowed
            continue
        yield tarinfo

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

async def time_wrapped(func, *args, **kwargs):
    logger.info("transfer started")
    start_time = time.perf_counter()
    ret = await func(*args, **kwargs)
    elapsed_time = time.perf_counter() - start_time
    logger.info("transfer completed in %ss", elapsed_time)
    if isinstance(ret, Path):
        size_mb = ret.stat().st_size / 1024 / 1024
        logger.info("%s: data size: %sMB, transfer rate %sMB/s", ret.name, size_mb, size_mb / elapsed_time)
    return ret

async def download_data():
    logger.info("retrieving data from simcore...")
    start_time = time.perf_counter()
    PORTS = node_ports.ports()
    inputs_path = Path(_INPUTS_FOLDER).expanduser()
    data = {}

    # let's gather all the data
    download_tasks = [time_wrapped(port.get) for port in PORTS.inputs if port and port.value]
    results = await asyncio.gather(*download_tasks)
    logger.info("completed download")
    # if there are files, move them to the final destination
    # if data, copy it to a json file
    for idx, port in enumerate(PORTS.inputs):
        if not port or not port.value:
            continue
        value = results[idx]
        data[port.key] = {"key": port.key, "value": value}

        if _FILE_TYPE_PREFIX in port.type:
            downloaded_file = value
            dest_path = inputs_path / port.key
            # first cleanup
            logger.info("removing %s", dest_path)
            shutil.rmtree(dest_path)
            if not downloaded_file:
                # the link may be empty
                continue
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

    data_file = inputs_path / _KEY_VALUE_FILE_NAME
    data_file.write_text(json.dumps(data))
    stop_time = time.perf_counter()
    logger.info("all data retrieved from simcore in %sseconds: %s", stop_time - start_time, data)

async def upload_data():
    logger.info("uploading data to simcore...")
    start_time = time.perf_counter()
    PORTS = node_ports.ports()
    outputs_path = Path(_OUTPUTS_FOLDER).expanduser()
    upload_tasks = []
    temp_files = []
    for port in PORTS.outputs:
        logger.debug("uploading data to port '%s' with value '%s'...", port.key, port.value)
        if _FILE_TYPE_PREFIX in port.type:
            src_folder = outputs_path / port.key
            list_files = list(src_folder.glob("*"))
            if len(list_files) == 1:
                # special case, direct upload
                upload_tasks.append(time_wrapped(port.set, list_files[0]))
                continue
            # generic case let's create an archive
            if len(list_files) > 1:
                temp_file = tempfile.NamedTemporaryFile(suffix=".tgz")
                temp_file.close()
                for _file in list_files:
                    with tarfile.open(temp_file.name, mode='w:gz') as tar_ptr:
                        for file_path in list_files:
                            tar_ptr.add(str(file_path), arcname=file_path.name, recursive=False)
                temp_files.append(temp_file.name)
                upload_tasks.append(time_wrapped(port.set, temp_file.name))
        else:
            data_file = outputs_path / _KEY_VALUE_FILE_NAME
            if data_file.exists():
                data = json.loads(data_file.read_text())
                if port.key in data and data[port.key] is not None:
                    upload_tasks.append(time_wrapped(port.set, data[port.key]))

        try:
            await asyncio.gather(*upload_tasks)
        finally:
            # clean up possible compressed files
            for file_path in temp_files:
                Path(file_path).unlink()
    stop_time = time.perf_counter()
    logger.info("all data uploaded to simcore in %sseconds", stop_time-start_time)


class RetrieveHandler(IPythonHandler):
    def initialize(self): #pylint: disable=no-self-use
        PORTS = node_ports.ports()
        _create_ports_sub_folders(PORTS.inputs, Path(_INPUTS_FOLDER).expanduser())
        _create_ports_sub_folders(PORTS.outputs, Path(_OUTPUTS_FOLDER).expanduser())

    async def get(self):
        try:
            await asyncio.gather(download_data(), upload_data())
            self.set_status(200)
        except node_ports.exceptions.NodeportsException as exc:
            logger.exception("Unexpected problem when processing retrieve call")
            self.set_status(500, reason=str(exc))
        except Exception: #pylint: disable=broad-except
            logger.exception("Unexpected problem when processing retrieve call")
            self.set_status(500)
        finally:
            self.finish('completed retrieve!')

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

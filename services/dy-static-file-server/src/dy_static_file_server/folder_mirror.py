# TODO: have a watcher doing all the watching
import hashlib
import logging
import os
import time
from pathlib import Path
from threading import Thread
from typing import Dict, List, Optional

from watchdog.events import DirModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class UnifyingEventHandler(FileSystemEventHandler):
    def __init__(self, input_dir: Path, output_dir: Path):
        super().__init__()
        self.input_dir: Path = input_dir
        self.output_dir: Path = output_dir

    def on_any_event(self, event: DirModifiedEvent):
        super().on_any_event(event)
        sync_directories_content(self.input_dir, self.output_dir)


def _list_files_in_dir(path: Path) -> List[Path]:
    return [x for x in path.rglob("*") if x.is_file()]


def _relative_file_names_mapping(
    containing_dir: Path, files: List[Path]
) -> Dict[str, Path]:
    containing_dir_str = str(containing_dir)

    def _relative_file_name(file: Path) -> str:
        return str(file).replace(containing_dir_str, "").strip("/")

    return {_relative_file_name(f): f for f in files}


def _checksum(file: Path) -> str:
    with open(file, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)

    return file_hash.hexdigest()


def _chunked_copy(input_file: Path, output_file: Path, chunk_size: int = 8192) -> None:
    logger.info("Copy %s -> %s", input_file, output_file)
    # ensure output destination diretory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(input_file, "rb") as in_f, open(output_file, "wb") as out_f:
        chunk = in_f.read(chunk_size)
        while chunk:
            out_f.write(chunk)
            chunk = in_f.read(chunk_size)


def sync_directories_content(input_dir: Path, output_dir: Path) -> None:
    logger.info("Running directory sync")
    files_in_input_dir = _list_files_in_dir(input_dir)
    files_in_output_dir = _list_files_in_dir(output_dir)

    input_relative_mapping = _relative_file_names_mapping(input_dir, files_in_input_dir)
    output_relative_mapping = _relative_file_names_mapping(
        output_dir, files_in_output_dir
    )

    # copy new files if they do not exist
    for file_name in input_relative_mapping:
        input_file = input_relative_mapping[file_name]
        # where to expect the output file
        expected_output_file = output_dir / file_name

        if input_file not in output_relative_mapping:
            _chunked_copy(input_file, expected_output_file)
            continue

        if _checksum(input_file) == _checksum(expected_output_file):
            _chunked_copy(input_file, expected_output_file)
            continue

    # remove files not existing files form outputs
    files_to_remove = set(output_relative_mapping.keys()) - set(
        input_relative_mapping.keys()
    )
    for relative_key in files_to_remove:
        file_path: Path = output_relative_mapping[relative_key]
        file_path.unlink()


def get_path_from_env(env_var_name: str) -> Path:
    str_path = os.environ.get(env_var_name, "")
    if len(str_path) == 0:
        raise ValueError(f"{env_var_name} could not be found or is empty")

    path = Path(str_path)
    if not path.is_dir():
        raise ValueError(f"{env_var_name}={str_path} is not a valid dir path")
    if not path.exists():
        raise ValueError(f"{env_var_name}={str_path} does not exist")
    return path


class FolderMirror:
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir: Path = input_dir
        self.output_dir: Path = output_dir

        self._keep_running = True
        self._thread: Optional[Thread] = None

    def _runner(self) -> None:
        event_handler = UnifyingEventHandler(
            input_dir=self.input_dir, output_dir=self.output_dir
        )
        observer = Observer()
        observer.schedule(event_handler, str(self.input_dir), recursive=True)
        observer.start()
        try:
            logger.info("FolderMonitor started")
            while self._keep_running:
                time.sleep(0.5)
        finally:
            observer.stop()
            observer.join()
        logger.info("FolderMonitor stopped")

    def start(self) -> None:
        self._keep_running = True
        self._thread = Thread(target=self._runner, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._keep_running = False
        if self._thread:
            self._thread.join()
            self._thread = None

    def join(self) -> None:
        if self._thread:
            self._thread.join()
        else:
            raise RuntimeError(f"{self.__class__.__name__} was not started")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    input_dir = get_path_from_env("DY_SIDECAR_PATH_INPUTS")
    output_dir = get_path_from_env("DY_SIDECAR_PATH_OUTPUTS")
    if input_dir == output_dir:
        raise ValueError(f"Inputs and outputs directories match {input_dir}")

    folder_monitor = FolderMirror(input_dir, output_dir)
    folder_monitor.start()
    folder_monitor.join()

    logger.info("%s main exited", FolderMirror.__name__)


if __name__ == "__main__":
    main()
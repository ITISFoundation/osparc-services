import logging
import json
import os
import time
from pathlib import Path
from threading import Thread
from typing import List, Optional
from subprocess import check_output
from watchdog.events import DirModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

# when not testing `dy_static_file_server` directory is not detected
# as a module; relative imports will not work
try:
    from index_html_generator import generate_index
except ModuleNotFoundError:
    from .index_html_generator import generate_index

logger = logging.getLogger(__name__)


class CouldNotDetectFilesException(Exception):
    pass


class UnifyingEventHandler(FileSystemEventHandler):
    def __init__(self, input_dir: Path, output_dir: Path):
        super().__init__()
        self.input_dir: Path = input_dir
        self.output_dir: Path = output_dir

    def on_any_event(self, event: DirModifiedEvent):
        super().on_any_event(event)
        logger.info("Detected event: %s", event)
        remap_input_to_output(self.input_dir, self.output_dir)
        # alway regenerate index
        generate_index()


def _list_files_in_dir(path: Path) -> List[Path]:
    return [x for x in path.rglob("*") if x.is_file()]


def _log_files_in_path(path: Path) -> None:
    split_command = f"ls -lah {path}".split(" ")
    command_result = check_output(split_command).decode("utf-8")
    logger.info("Files in '%s':\n%s", path, command_result)


def _wait_for_paths_to_be_present_on_disk(
    *paths: Path,
    basedir: Path,
    check_interval: float = 0.1,
    max_attempts: int = 100,
) -> None:
    total_run_time = max_attempts * check_interval
    logger.info(
        "Will check for %s seconds every %s seconds", total_run_time, check_interval
    )

    for _ in range(max_attempts):
        paths_are_not_missing = True
        for path in paths:
            if not path.exists():
                paths_are_not_missing = False
        logger.info("Are paths present? %s", paths_are_not_missing)

        if paths_are_not_missing:
            return
        time.sleep(check_interval)

    _log_files_in_path(basedir)
    raise CouldNotDetectFilesException("Did not find expected files on disk!")


def remap_input_to_output(input_dir: Path, output_dir: Path) -> None:
    logger.info("Running directory sync")

    input_file: Path = input_dir / "file_input" / "test_file"
    inputs_key_values_file = input_dir / "key_values.json"

    # When IO is slower the files may not already be present at the destination.
    # Poll files to see when they are present or raise an error if missing
    _wait_for_paths_to_be_present_on_disk(
        input_file, inputs_key_values_file, basedir=input_dir
    )

    _log_files_in_path(input_dir)
    _log_files_in_path(output_dir)

    # remove all presnet files in outputs
    files_in_output_dir = _list_files_in_dir(output_dir)
    for output_file in files_in_output_dir:
        output_file.unlink()

    # move file to correct path
    output_file_path: Path = output_dir / "file_output" / "test_file"
    if input_file.is_file():
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        output_file_path.write_bytes(input_file.read_bytes())

    # rewrite key_values.json
    inputs_key_values = json.loads(inputs_key_values_file.read_text())
    outputs_key_values = {
        k.replace("_input", "_output"): v["value"] for k, v in inputs_key_values.items()
    }
    if input_file.is_file():
        outputs_key_values["file_output"] = f"{output_file_path}"

    outputs_key_values_file = output_dir / "key_values.json"
    outputs_key_values_file.write_text(
        json.dumps(outputs_key_values, sort_keys=True, indent=4)
    )


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


class InputsObserver:
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

    is_legacy = os.environ.get("SIMCORE_NODE_BASEPATH", None) is not None

    input_dir = get_path_from_env(
        "INPUT_FOLDER" if is_legacy else "DY_SIDECAR_PATH_INPUTS"
    )
    output_dir = get_path_from_env(
        "OUTPUT_FOLDER" if is_legacy else "DY_SIDECAR_PATH_OUTPUTS"
    )
    if input_dir == output_dir:
        raise ValueError(f"Inputs and outputs directories match {input_dir}")

    # make sure index exists before the monitor starts
    generate_index()

    # start monitor that copies files in case they something
    inputs_objserver = InputsObserver(input_dir, output_dir)
    inputs_objserver.start()
    inputs_objserver.join()

    logger.info("%s main exited", InputsObserver.__name__)


if __name__ == "__main__":
    main()
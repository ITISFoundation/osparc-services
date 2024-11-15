import os
import asyncio
import json
import logging
import hashlib
from pathlib import Path
from typing import Tuple, Final, List, Dict


_logger = logging.getLogger(__name__)

DEFAULT_MONITOR_WAIT_INTERVAL: Final[float] = 1

# when not testing `dy_static_file_server` directory is not detected
# as a module; relative imports will not work
try:
    from index_html_generator import generate_index
except ModuleNotFoundError:
    from .index_html_generator import generate_index


def _get_file_info(filepath: Path) -> Tuple[str, float]:
    # Get file access and modification times
    file_stats = filepath.stat()
    modification_time = file_stats.st_mtime  # Last modification time

    # Calculate SHA-256 hash of the file content
    hash_sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    file_hash = hash_sha256.hexdigest()

    return file_hash, modification_time


def _list_files_in_dir(path: Path) -> List[Path]:
    return [x for x in path.rglob("*") if x.is_file()]


def _get_directory_state(directory: Path) -> Dict[Path, Tuple[str, float]]:
    return {p: _get_file_info(p) for p in _list_files_in_dir(directory)}


def remap_input_to_output(input_dir: Path, output_dir: Path) -> None:
    _logger.info("Attempt inputs to outputs sync")

    input_file: Path = input_dir / "file_input" / "test_file"
    inputs_key_values_file = input_dir / "key_values.json"

    # remove all present files in outputs
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

    _logger.info("inputs to outputs sync successful!")


class PortsMonitor:
    def __init__(
        self, input_dir: Path, output_dir: Path, *, monitor_interval: float = DEFAULT_MONITOR_WAIT_INTERVAL
    ) -> None:
        self.input_dir: Path = input_dir
        self.output_dir: Path = output_dir
        self.paths: set[Path] = {input_dir, output_dir}
        self.monitor_interval: float = monitor_interval

        self._monitor_task: asyncio.Task | None = None
        self._keep_running: bool = False

    def _get_state(self) -> Dict[Path, Dict[Path, Tuple[str, float]]]:
        """return aggravated state for all monitored paths"""
        return {p: _get_directory_state(p) for p in self.paths}

    async def _monitor(self) -> None:

        _logger.info("Started monitor")
        previous_state = self._get_state()

        while self._keep_running:
            await asyncio.sleep(self.monitor_interval)

            _logger.info("Checking")
            current_state = self._get_state()

            if previous_state != current_state:
                _logger.info("Change detected!")
                await self.on_change()

            previous_state = current_state

        _logger.info("Stopped monitor")

    async def on_change(self) -> None:
        try:
            remap_input_to_output(self.input_dir, self.output_dir)
            # alway regenerate index
            generate_index()
            _logger.info("on_change completed")
        except Exception as e:
            _logger.error("Could not finish remap of inputs to outputs %s", e)

    async def start(self) -> None:
        self._keep_running = True
        self._monitor_task = asyncio.create_task(self._monitor())

    async def stop(self) -> None:
        if self._monitor_task:
            self._keep_running = False
            await self._monitor_task
            self._monitor_task = None


async def _run_background_sync(input_dir: Path, output_dir: Path) -> None:
    monitor = PortsMonitor(input_dir, output_dir)
    await monitor.start()
    while True:
        await asyncio.sleep(1)


def _get_path_from_env(env_var_name: str) -> Path:
    str_path = os.environ.get(env_var_name, "")
    if len(str_path) == 0:
        raise ValueError(f"{env_var_name} could not be found or is empty")

    path = Path(str_path)
    if not path.is_dir():
        raise ValueError(f"{env_var_name}={str_path} is not a valid dir path")
    if not path.exists():
        raise ValueError(f"{env_var_name}={str_path} does not exist")
    return path


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    is_legacy = os.environ.get("SIMCORE_NODE_BASEPATH", None) is not None

    input_dir = _get_path_from_env(
        "INPUT_FOLDER" if is_legacy else "DY_SIDECAR_PATH_INPUTS"
    )
    output_dir = _get_path_from_env(
        "OUTPUT_FOLDER" if is_legacy else "DY_SIDECAR_PATH_OUTPUTS"
    )
    if input_dir == output_dir:
        raise ValueError(f"Inputs and outputs directories match {input_dir}")

    # make sure index exists before the monitor starts
    generate_index()
    asyncio.run(_run_background_sync(input_dir, output_dir))


if __name__ == "__main__":
    main()

# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
import hashlib
import time
from pathlib import Path
from threading import Thread
from types import ModuleType
from typing import Callable, Dict, List
from unittest.mock import patch
from _pytest.monkeypatch import MonkeyPatch

import pytest

# UTILS


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    assert path.exists() is True
    assert path.is_dir()
    return path


def _list_files_in_dir(path: Path) -> Dict[str, Path]:
    containing_dir_str = str(path)

    def _relative_file_name(file: Path) -> str:
        return str(file).replace(containing_dir_str, "").strip("/")

    return {_relative_file_name(f): f for f in path.rglob("*") if f.is_file()}


def _checksum(file: Path) -> str:
    with open(file, "rb") as f:
        file_hash = hashlib.sha256()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)

    return file_hash.hexdigest()


def assert_correct_transformation(
    input_dir: Path, output_dir: Path, key_values_json_outputs_content: str
) -> None:
    input_files = _list_files_in_dir(input_dir)
    output_files = _list_files_in_dir(output_dir)

    assert len(input_files) == len(output_files)

    inputs_test_file = input_dir / "file_input" / "test_file"
    outputs_test_file = output_dir / "file_output" / "test_file"

    assert inputs_test_file.is_file()
    assert outputs_test_file.is_file()
    assert _checksum(inputs_test_file) == _checksum(outputs_test_file)

    inputs_key_values = input_dir / "key_values.json"
    outputs_key_values = output_dir / "key_values.json"
    assert inputs_key_values.is_file()
    assert outputs_key_values.is_file()

    assert outputs_key_values.read_text() == key_values_json_outputs_content


# FIXTURES


@pytest.fixture
def input_dir(tmp_dir) -> Path:
    return _ensure_dir(tmp_dir / "input_dir")


@pytest.fixture
def output_dir(tmp_dir) -> Path:
    return _ensure_dir(tmp_dir / "output_dir")


@pytest.fixture
def env_vars(monkeypatch: MonkeyPatch, input_dir: Path, output_dir: Path) -> None:
    monkeypatch.setenv("DY_SIDECAR_PATH_INPUTS", str(input_dir))
    monkeypatch.setenv("DY_SIDECAR_PATH_OUTPUTS", str(output_dir))


@pytest.fixture
def same_input_and_output_dir(monkeypatch: MonkeyPatch, tmp_dir: Path) -> None:
    monkeypatch.setenv("DY_SIDECAR_PATH_INPUTS", str(tmp_dir))
    monkeypatch.setenv("DY_SIDECAR_PATH_OUTPUTS", str(tmp_dir))


@pytest.fixture
def inputs_validation_files(validation_dir: Path) -> List[Path]:
    return [
        validation_dir / "input" / "inputs_dynamic-sidecar-compose-spec.json",
        validation_dir / "input" / "inputs_dynamic-sidecar.json",
    ]


@pytest.fixture
def outputs_validation_files(validation_dir: Path) -> List[Path]:
    return [
        validation_dir / "output" / "outputs_dynamic-sidecar-compose-spec.json",
        validation_dir / "output" / "outputs_dynamic-sidecar.json",
    ]


@pytest.fixture
def key_values_json_inputs_content(validation_dir: Path, input_dir: Path) -> str:
    key_values_file = validation_dir / "input" / "inputs_dynamic-sidecar.json"
    return key_values_file.read_text().replace("{{INPUTS_FULL_PATH}}", f"{input_dir}")


@pytest.fixture
def key_values_json_outputs_content(validation_dir: Path, output_dir: Path) -> str:
    key_values_file = validation_dir / "output" / "outputs_dynamic-sidecar.json"
    return key_values_file.read_text().replace("{{OUTPUTS_FULL_PATH}}", f"{output_dir}")


@pytest.fixture
def create_files_in_input(key_values_json_inputs_content: str) -> Callable:
    def _callable(input_dir: Path) -> None:
        key_values = input_dir / "key_values.json"
        key_values.write_text(key_values_json_inputs_content)

        subdir = _ensure_dir(input_dir / "file_input")
        file_two = subdir / "test_file"
        file_two.write_text("some text here")

    return _callable


# TESTS


def test_ensure_same_content_in_validation_files(
    inputs_validation_files: List[Path],
    outputs_validation_files: List[Path],
) -> None:
    # ensure files exist
    for path in inputs_validation_files + outputs_validation_files:
        assert path.is_file()

    # check if content is the same
    message = "File content does not match for %s"
    assert len({x.read_text() for x in inputs_validation_files}) == 1, message % [
        x.name for x in inputs_validation_files
    ]
    assert len({x.read_text() for x in outputs_validation_files}) == 1, message % [
        x.name for x in outputs_validation_files
    ]


def test_can_import_module(dy_static_file_server: ModuleType) -> None:
    from dy_static_file_server import inputs_to_outputs

    assert type(inputs_to_outputs) == ModuleType


def test_folder_mirror(
    dy_static_file_server: ModuleType,
    input_dir: Path,
    output_dir: Path,
    create_files_in_input: Callable,
    key_values_json_outputs_content: str,
    env_server_root: None,
) -> None:
    from dy_static_file_server.inputs_to_outputs import InputsObserver

    inputs_observer = InputsObserver(input_dir, output_dir)
    inputs_observer.start()

    # give background thread time to start and copy
    time.sleep(0.01)
    create_files_in_input(input_dir)
    time.sleep(0.25)

    assert_correct_transformation(
        input_dir, output_dir, key_values_json_outputs_content
    )

    inputs_observer.stop()


def test_folder_mirror_join(
    dy_static_file_server: ModuleType, input_dir: Path, output_dir: Path
) -> None:
    from dy_static_file_server.inputs_to_outputs import InputsObserver

    inputs_observer = InputsObserver(input_dir, output_dir)

    # raises error if not started
    with pytest.raises(RuntimeError) as exec:  # pylint: disable=redefined-builtin
        inputs_observer.join()
    assert exec.value.args[0] == "InputsObserver was not started"

    # can be stopped from different thread while awaiting
    def _stop_after_delay(inputs_observer: InputsObserver) -> None:
        time.sleep(0.1)
        inputs_observer.stop()

    th = Thread(target=_stop_after_delay, args=(inputs_observer,), daemon=True)
    th.start()

    inputs_observer.start()
    inputs_observer.join()

    th.join()


def test_folder_mirror_main(
    dy_static_file_server: ModuleType, input_dir: Path, output_dir: Path, env_vars: None
) -> None:

    from dy_static_file_server import inputs_to_outputs

    with patch.object(inputs_to_outputs.InputsObserver, "join", return_value=None):
        inputs_to_outputs.main()


def test_folder_mirror_main(
    dy_static_file_server: ModuleType, tmp_dir: Path, same_input_and_output_dir: None
) -> None:

    from dy_static_file_server import inputs_to_outputs

    with pytest.raises(ValueError) as exec:  # pylint: disable=redefined-builtin
        inputs_to_outputs.main()
    assert exec.value.args[0] == f"Inputs and outputs directories match {tmp_dir}"
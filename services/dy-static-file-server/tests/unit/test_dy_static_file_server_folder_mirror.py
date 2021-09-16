# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
import hashlib
import time
from pathlib import Path
from threading import Thread
from types import ModuleType
from typing import Dict
from unittest.mock import patch
from _pytest.monkeypatch import MonkeyPatch

import pytest

# UTILS


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    assert path.exists() is True
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


def assert_same_dir_content(input_dir: Path, output_dir: Path) -> None:
    input_files = _list_files_in_dir(input_dir)
    output_files = _list_files_in_dir(output_dir)

    assert input_files.keys() == output_files.keys()

    for key in input_files.keys():
        input_file = input_files[key]
        output_file = output_files[key]

        assert _checksum(input_file) == _checksum(output_file)


def create_files_in_input(input_dir: Path) -> None:
    file_one = input_dir / "first_file.txt"
    file_one.write_text("hello_there")
    file_one.write_text("other stuff here")

    subdir = _ensure_dir(input_dir / "subdir")
    file_two = subdir / "second_file.txt"
    file_two.write_text("hello_there")
    file_two.write_text("other stuff here")


def remova_all_files_from_input(input_dir: Path) -> None:
    for file in _list_files_in_dir(input_dir).values():
        file.unlink()


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


# TESTS


def test_can_import_module(dy_static_file_server: ModuleType) -> None:
    from dy_static_file_server import folder_mirror

    assert type(folder_mirror) == ModuleType


def test_folder_mirror(
    dy_static_file_server: ModuleType, input_dir: Path, output_dir: Path
) -> None:
    from dy_static_file_server.folder_mirror import FolderMirror

    folder_mirror = FolderMirror(input_dir, output_dir)

    folder_mirror.start()

    create_files_in_input(input_dir)

    #  let the threads copy and sync the files
    time.sleep(0.25)
    assert_same_dir_content(input_dir, output_dir)

    # remove a file from input
    remova_all_files_from_input(input_dir)
    time.sleep(0.25)
    assert_same_dir_content(input_dir, output_dir)

    folder_mirror.stop()


def test_folder_mirror_join(
    dy_static_file_server: ModuleType, input_dir: Path, output_dir: Path
) -> None:
    from dy_static_file_server.folder_mirror import FolderMirror

    folder_mirror = FolderMirror(input_dir, output_dir)

    # raises error if not started
    with pytest.raises(RuntimeError) as exec:  # pylint: disable=redefined-builtin
        folder_mirror.join()
    assert exec.value.args[0] == "FolderMirror was not started"

    # can be stopped from different thread while awaiting
    def _stop_after_delay(folder_mirror: FolderMirror) -> None:
        time.sleep(0.1)
        folder_mirror.stop()

    th = Thread(target=_stop_after_delay, args=(folder_mirror,), daemon=True)
    th.start()

    folder_mirror.start()
    folder_mirror.join()

    th.join()


def test_folder_mirror_main(
    dy_static_file_server: ModuleType, input_dir: Path, output_dir: Path, env_vars: None
) -> None:

    from dy_static_file_server import folder_mirror

    with patch.object(folder_mirror.FolderMirror, "join", return_value=None):
        folder_mirror.main()


def test_folder_mirror_main(
    dy_static_file_server: ModuleType, tmp_dir: Path, same_input_and_output_dir: None
) -> None:

    from dy_static_file_server import folder_mirror

    with pytest.raises(ValueError) as exec:  # pylint: disable=redefined-builtin
        folder_mirror.main()
    assert exec.value.args[0] == f"Inputs and outputs directories match {tmp_dir}"
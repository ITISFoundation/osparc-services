# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name

import pytest
from pathlib import Path
from types import ModuleType
from typing import List
from _pytest.monkeypatch import MonkeyPatch

# UTILS


def _files_in_path(path: Path) -> List[Path]:
    # pylint: disable=unnecessary-comprehension
    return [x for x in path.rglob("*")]


# FIXTURES


@pytest.fixture
def mock_target_directory(
    dy_static_file_server: ModuleType, monkeypatch: MonkeyPatch, tmp_dir: Path
) -> None:
    from dy_static_file_server import ensure_random_workdir_data

    monkeypatch.setattr(ensure_random_workdir_data, "TARGET_DIRECTORY", tmp_dir)


# TESTS


def test_can_import_module(dy_static_file_server: ModuleType) -> None:
    from dy_static_file_server import ensure_random_workdir_data

    assert type(ensure_random_workdir_data) == ModuleType


def test_workdir_path_not_changed() -> None:
    from dy_static_file_server import ensure_random_workdir_data

    assert ensure_random_workdir_data.TARGET_DIRECTORY == Path("/workdir")


def test_main(mock_target_directory: None) -> None:
    from dy_static_file_server import ensure_random_workdir_data

    assert ensure_random_workdir_data.TARGET_DIRECTORY != Path("/workdir")

    assert len(_files_in_path(ensure_random_workdir_data.TARGET_DIRECTORY)) == 0

    ensure_random_workdir_data.main()

    assert len(_files_in_path(ensure_random_workdir_data.TARGET_DIRECTORY)) > 0


def test_no_file_changes(mock_target_directory: None) -> None:
    from dy_static_file_server import ensure_random_workdir_data

    ensure_random_workdir_data.main()
    first_run_files = _files_in_path(ensure_random_workdir_data.TARGET_DIRECTORY)

    ensure_random_workdir_data.main()
    second_run_files = _files_in_path(ensure_random_workdir_data.TARGET_DIRECTORY)

    assert set(first_run_files) == set(second_run_files)

# pytest: disable = redefined-outer-name

import pytest
from pathlib import Path
from types import ModuleType
import sys


@pytest.fixture
def tmp_dir(tmp_path) -> Path:
    return Path(tmp_path)


@pytest.fixture
def dy_static_file_server(src_dir: Path) -> ModuleType:
    # allow to search for the module
    # insert at 1, 0 is the script path (or '' in REPL)
    sys.path.insert(1, str(src_dir))

    import dy_static_file_server

    return dy_static_file_server
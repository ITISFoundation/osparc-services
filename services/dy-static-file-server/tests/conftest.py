# pylint:disable=unused-variable
# pylint:disable=unused-argument
# pylint:disable=redefined-outer-name

import sys
from pathlib import Path

import pytest

current_dir = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().parent


@pytest.fixture(scope="session")
def tests_dir() -> Path:
    assert current_dir.exists()
    return current_dir


@pytest.fixture(scope="session")
def validation_dir(project_slug_dir: Path) -> Path:
    validation_dir = project_slug_dir / "validation"
    assert validation_dir.exists()
    return validation_dir


@pytest.fixture(scope="session")
def project_slug_dir(tests_dir: Path) -> Path:
    project_slug_dir = tests_dir.parent
    assert project_slug_dir.exists()
    return project_slug_dir


@pytest.fixture(scope="session")
def src_dir(project_slug_dir: Path) -> Path:
    src_dir = project_slug_dir / "src"
    assert src_dir.exists()
    return src_dir


@pytest.fixture(scope="session")
def tools_dir(project_slug_dir: Path) -> Path:
    tools_dir = project_slug_dir / "tools"
    assert tools_dir.exists()
    return tools_dir


@pytest.fixture(scope="session")
def docker_dir(project_slug_dir: Path) -> Path:
    docker_dir = project_slug_dir / "docker"
    assert docker_dir.exists()
    return docker_dir


@pytest.fixture(scope="session")
def package_dir(src_dir: Path) -> Path:
    package_dir = src_dir / "name_of_the_project"
    assert package_dir.exists()
    return package_dir


@pytest.fixture(scope="session")
def metadata_dir(project_slug_dir: Path) -> Path:
    metadata_dir = project_slug_dir / "metadata"
    assert metadata_dir.exists()
    return metadata_dir


@pytest.fixture(
    scope="function",
    params=[
        "metadata.yml",
        "metadata-dynamic-sidecar.yml",
        "metadata-dynamic-sidecar-compose-spec.yml",
    ],
)
def metadata_file_name(request) -> str:
    return request.param


@pytest.fixture(scope="function")
def inputs_file_name_part(metadata_file_name: str) -> str:
    name_part = (
        metadata_file_name.replace("metadata-", "")
        .replace("metadata", "")
        .replace(".yml", "")
    )
    return "" if len(name_part) == 0 else f"_{name_part}"


@pytest.fixture(scope="function")
def metadata_file(metadata_dir: Path, metadata_file_name: str) -> Path:
    metadata_file = metadata_dir / metadata_file_name
    assert metadata_file.exists()
    return metadata_file


@pytest.fixture(scope="session")
def git_root_dir() -> Path:
    # finds where is .git
    root_dir = current_dir
    while root_dir.as_posix() != "/" and not Path(root_dir / ".git").exists():
        root_dir = root_dir.parent
    if root_dir.as_posix() == "/":
        return None
    return root_dir

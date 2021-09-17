# pylint:disable=unused-variable
# pylint:disable=unused-argument
# pylint:disable=redefined-outer-name

from pathlib import Path

import pytest

expected_files = (
    ".cookiecutterrc",
    ".dockerignore",
    ".gitignore",
    ".pylintrc",
    "metadata:metadata.yml",
    "metadata/metadata-dynamic-sidecar-compose-spec.yml",
    "metadata/metadata-dynamic-sidecar.yml",
    "metadata/metadata.yml",
    "docker/custom:nginx.conf",
    "docker/custom:boot.sh",
    "docker/custom:Dockerfile",
    "tools:update_compose_labels.py",
    "versioning:integration.cfg",
    "versioning:service.cfg",
    "requirements/base.in",
    "requirements/base.txt",
    "requirements/test.in",
    "requirements/test.txt",
    "static-content/hello-world.txt",
    "src/dy_static_file_server/__init__.py",
    "src/dy_static_file_server/inputs_to_outputs.py",
    "Makefile",
    "VERSION",
    "README.md",
    "docker-compose-build.yml",
    "docker-compose-meta.yml",
    "docker-compose.devel.yml",
    "docker-compose.yml",
)


@pytest.mark.parametrize("expected_path", expected_files)
def test_path_in_repo(expected_path: str, project_slug_dir: Path):

    if ":" in expected_path:
        folder, glob = expected_path.split(":")
        folder_path = project_slug_dir / folder
        assert folder_path.exists(), f"folder {folder_path} is missing!"
        assert any(folder_path.glob(glob)), f"no {glob} in {folder_path}"
    else:
        assert (
            project_slug_dir / expected_path
        ).exists(), f"{expected_path} is missing from {project_slug_dir}"

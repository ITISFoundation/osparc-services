# pylint:disable=wildcard-import
# pylint:disable=unused-import
# pylint:disable=unused-variable
# pylint:disable=unused-argument
# pylint:disable=redefined-outer-name

from pathlib import Path

import pytest

def test_docker_dir(docker_dir: Path):
    labels_dir = docker_dir / "labels" 
    assert labels_dir.exists()

    labels = list(labels_dir.glob("*.json"))
    assert len(labels) > 0

    assert Path(docker_dir / "entrypoint.sh").exists()
    assert Path(docker_dir / "boot.sh").exists()

def test_tools_dir(tools_dir: Path):
    assert Path(tools_dir / "requirements.txt").exists()
    assert Path(tools_dir / "update_compose_labels.py").exists()
    assert Path(tools_dir / "run_creator.py").exists()

def test_package_dir(src_dir: Path):
    assert Path(src_dir / "Dockerfile").exists()

def test_slug_dir(project_slug_dir: Path):
    assert Path(project_slug_dir / ".bumpversion.cfg").exists()
    assert Path(project_slug_dir / ".env-devel").exists()
    assert Path(project_slug_dir / "docker-compose.yml").exists()
    assert Path(project_slug_dir / "Makefile").exists()
    assert Path(project_slug_dir / "README.md").exists()
    assert Path(project_slug_dir / "VERSION").exists()
# pylint:disable=wildcard-import
# pylint:disable=unused-import
# pylint:disable=unused-variable
# pylint:disable=unused-argument
# pylint:disable=redefined-outer-name

import json
import os
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Dict

import docker
import jsonschema

import pytest


@pytest.fixture
def docker_client() -> docker.DockerClient:
    return docker.from_env()

@pytest.fixture
def docker_image_key(docker_client: docker.DockerClient) -> str:
    image_key = "simcore/services/comp/cc-rabbit-2d:latest"
    docker_images = [image for image in docker_client.images.list() if any(image_key in tag for tag in image.tags)]
    return docker_images[0].tags[0]

@pytest.fixture
def docker_image(docker_client: docker.DockerClient, docker_image_key: str) -> docker.models.images.Image:
    docker_image = docker_client.images.get(docker_image_key)
    assert docker_image
    return docker_image

def _download_url(url: str, file: Path):
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(url) as response, file.open('wb') as out_file:
        shutil.copyfileobj(response, out_file)
    assert file.exists()

@pytest.fixture
def osparc_service_labels_jsonschema(tmp_path) -> Dict:
    url = "https://raw.githubusercontent.com/ITISFoundation/osparc-simcore/master/api/specs/shared/schemas/node-meta-v0.0.1.json"
    file_name = tmp_path / "service_label.json"
    _download_url(url, file_name)
    with file_name.open() as fp:
        json_schema = json.load(fp)
        return json_schema

def _convert_to_simcore_labels(image_labels: Dict) -> Dict:
    io_simcore_labels = {}
    for key, value in image_labels.items():
        if str(key).startswith("io.simcore."):
            simcore_label = json.loads(value)
            simcore_keys = list(simcore_label.keys())
            assert len(simcore_keys) == 1
            simcore_key = simcore_keys[0]
            simcore_value = simcore_label[simcore_key]
            io_simcore_labels[simcore_key] = simcore_value
    assert len(io_simcore_labels) > 0
    return io_simcore_labels


def test_docker_io_simcore_labels_against_files(docker_image: docker.models.images.Image, docker_dir):
    image_labels = docker_image.labels
    io_simcore_labels = _convert_to_simcore_labels(image_labels)
    # check files are identical
    for key, value in io_simcore_labels.items():
        file_name = Path(docker_dir / "labels" / "{}.json".format(key))
        assert file_name.exists()
        with file_name.open() as fp:
            label_dict = json.load(fp)
            assert key in label_dict
            assert value == label_dict[key]


def test_validate_docker_io_simcore_labels(docker_image: docker.models.images.Image, osparc_service_labels_jsonschema: Dict):
    image_labels = docker_image.labels
    # get io labels
    io_simcore_labels = _convert_to_simcore_labels(image_labels)
    # validate schema
    try:
        jsonschema.validate(io_simcore_labels, osparc_service_labels_jsonschema)
    except jsonschema.SchemaError:
        pytest.fail("Schema {} contains errors".format(osparc_service_labels_jsonschema))
    except jsonschema.ValidationError:
        pytest.fail("Failed to validate docker image io labels against schema")

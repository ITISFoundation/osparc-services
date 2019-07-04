# pylint:disable=wildcard-import
# pylint:disable=unused-import
# pylint:disable=unused-variable
# pylint:disable=unused-argument
# pylint:disable=redefined-outer-name

import filecmp
import json
import os
import shutil
import time
from pathlib import Path
from pprint import pformat
from typing import Dict

import docker
import pytest

_FOLDER_NAMES = ["input", "output", "log"]
_CONTAINER_FOLDER = Path("/home/scu/data")

@pytest.fixture
def docker_client() -> docker.DockerClient:
    return docker.from_env()

@pytest.fixture
def docker_image_key(docker_client: docker.DockerClient) -> str:
    registry = os.environ.get("DOCKER_REGISTRY", "itisfoundation")
    tag = os.environ.get("DOCKER_IMAGE_TAG", "latest")
    image_key = "{}/mattward-dash:{}".format(registry, tag)
    docker_images = [image for image in docker_client.images.list() if any(image_key in tag for tag in image.tags)]
    assert len(docker_images) == 1, "could not find docker image {}".format(image_key)
    return docker_images[0].tags[0]

@pytest.fixture
def dynamic_service_environ(env_devel: Dict):
    for key, value in env_devel.items():
        os.environ[key] = value


@pytest.fixture
def docker_container(dynamic_service_environ, docker_client: docker.DockerClient, docker_image_key: str) -> docker.models.containers.Container:
    # run the container (this may take some time)
    try:
        container_start_time = time.perf_counter()
        container = docker_client.containers.run(docker_image_key, detach=True, remove=False, init=True)
        while not container.status == "running":            
            if container.status == "exited":
                # not good for a dynamic container
                pytest.fail("The container exited already.\nlogs: {}".format(pformat(container.logs(timestamps=True).decode("UTF-8")).split("\n"), width=200))
            # wait
            time.sleep(1)
            container.reload()
        container_started_time = time.perf_counter()
        # should be less than 10sec
        assert (container_started_time - container_start_time) < 10
        yield container
    except docker.errors.ContainerError as exc:
        # the container did not run correctly
        pytest.fail("The container stopped with exit code {}\n\n\ncommand:\n {}, \n\n\nlog:\n{}".format(exc.exit_status,
            exc.command, pformat(
                (container.logs(timestamps=True).decode("UTF-8")).split("\n"), width=200
                )))
    finally:
        #cleanup
        container.stop()
        container.remove()

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

def test_run_container(docker_container: docker.models.containers.Container):
    container_labels = docker_container.labels
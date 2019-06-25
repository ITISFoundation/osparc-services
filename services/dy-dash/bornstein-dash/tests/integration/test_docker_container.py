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
from requests.exceptions import ReadTimeout


@pytest.fixture
def docker_client() -> docker.DockerClient:
    return docker.from_env()


@pytest.fixture
def docker_image_key(docker_client: docker.DockerClient) -> str:
    docker_registry = os.environ.get("DOCKER_REGISTRY", "itisfoundation")
    docker_image_tag = os.environ.get("DOCKER_IMAGE_TAG", "latest")
    image_key = "{}/bornstein-dash:{}".format(docker_registry, docker_image_tag)
    docker_images = [image for image in docker_client.images.list() if any(
        image_key in tag for tag in image.tags)]
    return docker_images[0].tags[0]

@pytest.fixture
def container_variables() -> Dict:
    # TODO SAN: set variables in a meaningfulway for dyn services
    # this means having a postgres, minio, storage running (similar to what dev mode does)
    env = {
        "SIMCORE_NODE_UUID": "-1",
        "SIMCORE_USER_ID": "-1",
        "SIMCORE_NODE_BASEPATH": "",
        "SIMCORE_NODE_APP_STATE_PATH": "/home/jovyan/notebooks",
        "STORAGE_ENDPOINT": "=1",
        "S3_ENDPOINT": "=1",
        "S3_ACCESS_KEY": "-1",
        "S3_SECRET_KEY": "-1",
        "S3_BUCKET_NAME": "-1",
        "POSTGRES_ENDPOINT": "-1",
        "POSTGRES_USER": "-1",
        "POSTGRES_PASSWORD": "-1",
        "POSTGRES_DB": "-1"
    }
    return env


@pytest.fixture
def docker_container(docker_client: docker.DockerClient, docker_image_key: str, container_variables: Dict) -> docker.models.containers.Container:
    # TODO SAN: here we need a swarm, then to start the container as a service instead of a container
    # TODO SAN: input should be pushed to database/s3 here
    # run the container (this may take some time)
    container = None
    try:
        container = docker_client.containers.run(docker_image_key,
                                                 detach=True, remove=False, environment=container_variables)
        # here we wait, this should be defined as the min time to wait for the container to be reactive
        time.sleep(5)
        # update the status
        container.reload()
        if container.status == "running":
            yield container
        else:
            pytest.fail("The container failed starting after 10secs, \n\n\nlog:\n{}".format(pformat(
                (container.logs(timestamps=True).decode("UTF-8")).split("\n"), width=200
            )))

    except ReadTimeout:
        pytest.fail("The container did not get into running state after 30seconds\n\nlog: {}".format(pformat(
            (container.logs(timestamps=True).decode("UTF-8")).split("\n"), width=200
        )))
    except docker.errors.ContainerError as exc:
        # the container did not run correctly
        pytest.fail("The container stopped with exit code {}\n\n\ncommand:\n {}, \n\n\nlog:\n{}".format(exc.exit_status,
                                                                                                        exc.command, pformat(
                                                                                                            (container.logs(timestamps=True).decode("UTF-8")).split("\n"), width=200
                                                                                                        )))
    finally:
        # cleanup
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
    # TODO SAN: based on labels check that the container runs on the right URL, etc...
    pass

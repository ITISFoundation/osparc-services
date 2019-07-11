#!/bin/python

""" Update a docker-compose file with json files in a path

    Usage: python update_compose_labels --c docker-compose.yml -f folder/path

:return: error code
"""

import argparse
import json
import logging
import sys
from enum import IntEnum
from pathlib import Path
from typing import Dict

import yaml

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ExitCode(IntEnum):
    SUCCESS = 0
    FAIL = 1

def get_compose_file(compose_file: Path) -> Dict:
    with compose_file.open() as filep:
        return yaml.safe_load(filep)


def stringify_file(input_file: Path) -> str:
    with input_file.open() as filep:
        return json.dumps(json.load(filep))


def stringify_folder(folder: Path) -> Dict:
    jsons = {}
    for json_file in folder.glob("*.json"):
        jsons["io.simcore.{}".format(json_file.stem)] = stringify_file(json_file)
    return jsons


def update_compose_labels(compose_cfg: Dict, json_labels: Dict) -> bool:
    compose_labels = compose_cfg["services"]["mattward-viewer"]["build"]["labels"]
    changed = False
    for json_key, json_value in json_labels.items():
        if json_key in compose_labels:
            if compose_labels[json_key] == json_value:
                continue
        compose_labels[json_key] = json_value
        changed = True
    return changed

def main(args = None) -> int:
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--compose", help="The compose file where labels shall be updated", type=Path, required=True)
        parser.add_argument("--input", help="The json folder to stringify", type=Path, required=True)
        options = parser.parse_args(args)


        log.info("Testing if %s needs updates using labels in %s", options.compose, options.input)
        # get available jsons
        compose_cfg = get_compose_file(options.compose)
        json_labels = stringify_folder(options.input)
        if update_compose_labels(compose_cfg, json_labels):
            log.info("Updating %s using labels in %s", options.compose, options.input)
            # write the file back
            with options.compose.open('w') as fp:
                yaml.safe_dump(compose_cfg, fp, default_flow_style=False)
                log.info("Update completed")
        else:
            log.info("No update necessary")
        return ExitCode.SUCCESS
    except: #pylint: disable=bare-except
        log.exception("Unexpected error:")
        return ExitCode.FAIL


if __name__ == "__main__":
    sys.exit(main())

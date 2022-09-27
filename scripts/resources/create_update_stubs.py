import json

from typing import List

import semver

import click

import os 

from pathlib import Path
dir_path = Path(os.path.dirname(os.path.realpath(__file__)))


TAB = "  "
O_BRACKET = "{"
C_BRACKET = "}"
QUOTE = "\""
SLASH = "/"

@click.command()
@click.option('--toc', help='File containing all servcies in this repo')
def create_update_stubs(toc: str):
    """Create a Dockerfile + docker-compose as a  basis"""
    compose_spec: List[str] = []
    dockerfile: List[str] = []

    with open("toc.json") as json_file:
        data = json.load(json_file)
        compose_spec.append("version: '3.6'")
        compose_spec.append("services:")
        settings_key = "simcore.service.settings"
        for key in data:
            service = data[key]
            if service["type"] == "dynamic":
                old_version = service['version']
                new_version = semver.VersionInfo.parse(
                    old_version).bump_patch()
                compose_spec.append(f"{TAB}{key}:")
                compose_spec.append(
                    f"{2*TAB}image: registry:5000/simcore/services/dynamic/{key}:{new_version}")
                compose_spec.append(f"{2*TAB}build:")
                compose_spec.append(f"{3*TAB}context: .")
                compose_spec.append(f"{3*TAB}dockerfile: Dockerfile")
                compose_spec.append(f"{3*TAB}target: {key}")
                compose_spec.append(f"{3*TAB}labels:")
                compose_spec.append(
                    f"{4*TAB}io.simcore.version: '{O_BRACKET}{QUOTE}version{QUOTE}: {QUOTE}{new_version}{QUOTE}{C_BRACKET}'")
                compose_spec.append(
                    f"{4*TAB}simcore.service.settings: '{json.dumps(service[settings_key])}'")
                compose_spec.append("")

                dockerfile.append(
                    f"FROM itisfoundation{SLASH}{key}:{old_version} as {key}")
                dockerfile.append("")

    with open(dir_path / "docker-compose.yml", 'w') as f:
        f.write("\n".join(compose_spec))

    with open(dir_path / "Dockerfile", 'w') as f:
        f.write("\n".join(dockerfile))

if __name__ == '__main__':
    create_update_stubs()

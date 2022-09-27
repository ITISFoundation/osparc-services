""" Creates a table of contents with all the services in this repository


"""
import json
import os
import pdb
import re
import sys
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from unittest import result

import yaml
from pytablewriter import MarkdownTableWriter

current_file: Path = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve()
current_dir: Path = current_file.parent
repo_dir: Path = current_dir.parent.parent
readme_path: Path = repo_dir / "README.md"
services_dir: Path = repo_dir / "services"
workflows_dir: Path = repo_dir / ".github/workflows"

timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def debug_it(fun):
    def wrap(*args, **kargs):
        try:
            return fun(*args, **kargs)
        except:  # pylint: disable=bare-except
            _extype, _value, tb = sys.exc_info()
            traceback.print_exc()
            pdb.post_mortem(tb)

    return wrap


def parse_repo():
    docker_files = defaultdict(dict)
    version_files = defaultdict(dict)
    services_info = defaultdict(dict)
    dockerfile_label_infos = defaultdict(dict)

    for base, _dirs, files in os.walk(services_dir):
        base = Path(base)
        relbase = os.path.relpath(base, services_dir)

        for file_name in files:
            if file_name == "Dockerfile":
                # A dockerfile defines an image
                title = os.path.basename(relbase)
                while title in ("src", "client", "server"):
                    title = os.path.basename(relbase.replace("/" + title, ""))
                title = re.sub(r"^(dy-)", "", title)

                docker_files[relbase].update({"title": title, "dockefile": relbase})

            elif file_name == "VERSION":
                # Every service is published with a name and a version
                version_files[relbase].update(
                    {"version": (base / "VERSION").read_text().strip()}
                )

            elif re.match(r"docker-compose[-meta|build]*.ya*ml", file_name):
                with open(f"{base}/{file_name}") as fh:
                    content = yaml.safe_load(fh)

                for service_name, service in content["services"].items():
                    info = {}

                    if "image" in service:
                        new_image = service["image"]
                        prev_image = services_info[service_name].get("image")
                        if prev_image and new_image.count("{") < prev_image.count("{"):
                            info["image"] = new_image
                        else:
                            info["image"] = new_image

                    if "build" in service:

                        if "dockerfile" in service["build"]:
                            context = service["build"].get("context", ".")
                            dockerfile = base / context / service["build"]["dockerfile"]
                            assert (
                                dockerfile.exists()
                            ), f"Invalid path for Dockerfile: {dockerfile}"
                            info["dockerfile"] = os.path.relpath(
                                dockerfile.resolve(), services_dir
                            )

                        if "labels" in service["build"]:
                            for key in [
                                "key",
                                "version",
                                "type",
                                "name",
                                "description",
                            ]:
                                info[key] = json.loads(
                                    service["build"]["labels"][f"io.simcore.{key}"]
                                )[key]
                            # dynamic service have an additional key: "simcore.service.settings"
                            settings_key = "simcore.service.settings"
                            if settings_key in service["build"]["labels"]:
                                try:
                                    settings_list = json.loads(service["build"]["labels"]["simcore.service.settings"].encode("utf8"))
                                except json.JSONDecodeError as e:
                                    print(f"Could not decode: {settings_list} for {service_name}") 
                                    print(e)
                                    continue
                                info["simcore.service.settings"] = settings_list

                    services_info[service_name].update(info)

    services_info_clean = {k: v for k, v in services_info.items() if "key" in v}

    def _get_closest_version_file(dockerfile: Path) -> Dict:
        max_score = 0
        result = None
        for relbase in version_files:
            parts = Path(relbase).parts
            score = 0
            try:
                for i, part in enumerate(Path(dockerfile).parts):
                    assert part == parts[i]
                    score += 1
            except (IndexError, AssertionError):
                pass
            if score > max_score:
                result = version_files[relbase]
        return result

    for service in services_info_clean.values():
        if service.get("version") == "${DOCKER_IMAGE_TAG}":
            dockerfile = service["dockerfile"]
            service["version"] = _get_closest_version_file(dockerfile)["version"]

    return services_info_clean


def get_github_workflows() -> List[Path]:
    return list(workflows_dir.glob("*.yml"))


def find_corresponding_workflow(
    service_info: Dict[str, str], workflow_files: List[Path]
) -> Optional[Path]:
    possible_names = [service_info["key"].split("/")[-1], service_info["name"]]
    for workflow in workflow_files:
        if any(name in workflow.stem for name in possible_names):
            return workflow


def create_markdown(services_info, workflow_files: List[Path], stream):
    writer = MarkdownTableWriter()
    writer.stream = stream
    writer.headers = ["name", "description", "type", "latest version", "build status"]
    writer.value_matrix = []
    for key in sorted(services_info.keys()):
        row = services_info[key]
        image_key = "{}:{}".format(row["key"].rsplit("/", 1)[-1], row["version"])
        # try to find the corresponding workflow
        workflow_file: Path = find_corresponding_workflow(row, workflow_files)
        writer.value_matrix.append(
            [
                "[{name}](services/{dockerfile})".format(**row),
                row["description"],
                row["type"],
                f"[![](https://images.microbadger.com/badges/version/itisfoundation/{image_key}.svg)](https://microbadger.com/images/itisfoundation/{image_key} 'See Image Version')",
                f"![{row['name']}](https://github.com/ITISFoundation/osparc-services/workflows/{workflow_file.stem}/badge.svg?branch=master)"
                if workflow_file
                else "",
            ]
        )

    writer.margin = 2  # add a whitespace for both sides of each cell
    writer.write_table()


TOC_BEGIN = r"<!-- TOC_BEGIN -->"
TOC_END = r"<!-- TOC_END -->"


def split_section(readme):
    """
    returns pre and post sections
    """
    begin = end = len(readme)
    for match in re.finditer(r"<\!--\s*TOC_(\w+)\s*-->", readme):
        name = match.group(1)
        if name == "BEGIN":
            begin = match.start(0)
        elif name == "END":
            end = match.end(0)
    assert begin <= end
    return readme[:begin], readme[end:]


def stamp_message():
    this_file = os.path.relpath(current_file, repo_dir)
    return f"<!-- Automaticaly produced by {this_file} on {timestamp} -->"


@debug_it
def main():
    services_info = parse_repo()
    workflow_files = get_github_workflows()

    with open("toc.json", "wt") as fh:
        json.dump(services_info, fh, indent=2, sort_keys=True)

    with open(readme_path) as fh:
        readme = fh.read()

    pre, post = split_section(readme)

    with open(readme_path, "w") as fh:
        print(pre.strip(), file=fh)

        print(TOC_BEGIN, file=fh)
        print(stamp_message(), file=fh)
        print("## Available services [%d]" % len(services_info), file=fh)
        create_markdown(services_info, workflow_files, fh)
        print(f"*Updated on {timestamp}*\n", file=fh)
        print(TOC_END, file=fh)

        print(post.strip(), file=fh)


if __name__ == "__main__":
    main()

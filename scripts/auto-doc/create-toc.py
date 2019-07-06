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
from pprint import pprint

import yaml
from pytablewriter import MarkdownTableWriter

current_file = Path( sys.argv[0] if __name__ == "__main__" else __file__).resolve()
current_dir = current_file.parent
repo_dir = current_dir.parent.parent
readme_path = repo_dir / "README.md"
services_dir = repo_dir / "services"

def debug_it(fun):
    def wrap(*args, **kargs):
        try:
            return fun(*args, **kargs)
        except:
            extype, value, tb = sys.exc_info()
            traceback.print_exc()
            pdb.post_mortem(tb)
    return wrap

def parse_repo():
    docker_files = defaultdict(dict)
    version_files = defaultdict(dict)
    services_info = defaultdict(dict)

    for base, dirs, files in os.walk(services_dir):
        relbase = os.path.relpath(base, services_dir)
        for file_name in files:
            if file_name == "Dockerfile":
                # A dockerfile defines an image
                title = os.path.basename(relbase)
                while title in ('src', 'client', 'server'):
                    title = os.path.basename(relbase.replace("/"+title, ""))
                title = re.sub(r'^(dy-)', "", title)

                docker_files[relbase].update({
                    'title': title,
                    'folder': relbase
                })

            elif file_name == "VERSION":
                # Every service is published with a name and a version
                version_files[relbase].update({
                    'version': open(f"{base}/VERSION").read().strip()
                })

            elif file_name == "docker-compose.yml":
                with open(f"{base}/docker-compose.yml") as fh:
                    content = yaml.safe_load(fh)

                for service_name, service in content['services'].items():
                    if 'labels' in service['build']:
                        info = {
                            'folder': f'services/{relbase}/' + os.path.dirname(service['build'].get('dockerfile','')),
                            'image': service['image']
                        }

                        for key in ['key', 'version', 'type', 'name', 'description']:
                            info[key] = json.loads(service['build']['labels'][f'io.simcore.{key}'])[key]
                        services_info[service_name].update(info)

    return services_info


def create_markdown(services_info, stream):
    writer = MarkdownTableWriter()
    writer.stream = stream
    writer.headers = ['name', 'description', 'type', 'latest version', 'identifier']
    writer.value_matrix = []
    for key in sorted(services_info.keys()):
        row = services_info[key]
        writer.value_matrix.append( [
            "[{name}]({folder})".format(**row),
            row['description'],
            row['type'],
            row['version'],
            "{key}:{version}".format(**row),
        ] )

    writer.margin = 2  # add a whitespace for both sides of each cell
    writer.write_table()


def split_section(readme):
    for match in re.finditer(r'<\!--\s*TOC_(\w+)\s*-->', readme):
        name = match.group(1)
        if name == "BEGIN":
            begin = match.end(0)+1
        elif name == "END":
            end = match.start(0)
    assert begin<=end, "TOC_BEGIN, TOC_END missing?"
    return readme[:begin], readme[end:]

def stamp_message():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    this_file = os.path.relpath(current_file, repo_dir)
    return f"<!-- Automaticaly produced by {this_file} on {timestamp} -->"

@debug_it
def main():
    services_info = parse_repo()

    print(json.dumps(services_info, indent=3, sort_keys=True))

    with open(readme_path) as fh:
        readme = fh.read()

    pre, post = split_section(readme)

    with open(readme_path, 'w') as fh:
        print(pre, file=fh)
        print(stamp_message(), file=fh)
        print("## Available services", file=fh)
        create_markdown(services_info, fh)
        print(post, file=fh)

if __name__ == "__main__":
    main()

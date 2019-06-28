#!/bin/python

""" Creates a bash script that uses jq tool to retrieve variables
    to use in bash from a json file for use in an osparc service.

    Usage python run_creator --folder path/to/inputs.json --runscript path/to/put/the/script
:return: error code
"""


import argparse
import json
import logging
import sys
from enum import IntEnum
from pathlib import Path
from typing import Dict

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ExitCode(IntEnum):
    SUCCESS = 0
    FAIL = 1


def get_input_config(folder: Path) -> Dict:
    with (folder / "inputs.json").open() as fp:
        return json.load(fp)

def main(args = None) -> int:
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--folder", help="The json folder where to find the labels", type=Path, required=True)
        parser.add_argument("--runscript", help="The run script", type=Path, required=True)
        options = parser.parse_args(args)

        # generate variables for input
        input_script = [
            "#!/bin/bash",
            "#---------------------------------------------------------------",
            "# AUTO-GENERATED CODE, do not modify this will be overwritten!!!",
            "#---------------------------------------------------------------",
            "set -e",
            "_json_input=$INPUT_FOLDER/input.json"
            ]
        input_config = get_input_config(options.folder)
        for input_key, input_value in input_config["inputs"].items():
            if "data:" in input_value["type"]:
                filename = input_key
                if "fileToKeyMap" in input_value and len(input_value["fileToKeyMap"]) > 0:
                    filename,_ = next(iter(input_value["fileToKeyMap"].items()))
                input_script.append("export {}=$INPUT_FOLDER/{}".format(str(input_key).upper(), str(filename)))
            else:
                input_script.append("export {}=$(cat $_json_input | jq '.{}')".format(str(input_key).upper(), input_key))

        input_script.extend([
            "export LOG_FILE=$LOG_FOLDER/log.dat",
            "bash execute"
        ])

        # write shell script
        shell_script = str("\n").join(input_script)
        options.runscript.write_text(shell_script)
        return ExitCode.SUCCESS
    except: #pylint: disable=bare-except
        log.exception("Unexpected error:")
        return ExitCode.FAIL

if __name__ == "__main__":
    sys.exit(main())

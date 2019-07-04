# pylint:disable=wildcard-import
# pylint:disable=unused-import
# pylint:disable=unused-variable
# pylint:disable=unused-argument
# pylint:disable=redefined-outer-name

import os
import re
import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope='session')
def pylintrc(git_root_dir: Path):
    if not git_root_dir:
        # we are not in a git repo here...
        return None
    pylintrcs = list(git_root_dir.glob("**/.pylintrc"))
    assert len(pylintrcs) > 0
    pylintrc = pylintrcs[0]
    assert pylintrc.exists()
    return pylintrc

def test_run_pylint(pylintrc, package_dir):
    if list(package_dir.glob("**/*.py")):
        if pylintrc:
            cmd = 'pylint -j 4 --rcfile {} -v {}'.format(pylintrc, package_dir)
        else:
            cmd = 'pylint -j 4 -v {}'.format(package_dir)
        assert subprocess.check_call(cmd.split()) == 0

def test_no_pdbs_in_place(package_dir):
    MATCH = re.compile(r'pdb.set_trace()')
    EXCLUDE = ["__pycache__", ".git"]
    for root, dirs, files in os.walk(package_dir):
        for name in files:
            if name.endswith(".py"):
                pypth = (Path(root) / name)
                code = pypth.read_text()
                found = MATCH.findall(code)
                assert not found, "pbd.set_trace found in %s" % pypth
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
    
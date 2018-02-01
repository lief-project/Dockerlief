#!/usr/bin/env python3.6
import sys
import os
import logging
import pathlib
import subprocess
import shutil

LOG_LEVEL = logging.DEBUG

logging.getLogger().addHandler(logging.StreamHandler())
logging.getLogger().setLevel(LOG_LEVEL)
logger = logging.getLogger(__name__)

CURRENTDIR = pathlib.Path(__file__).resolve().parent
REPODIR    = CURRENTDIR.parent
sys.path.insert(0, REPODIR.as_posix())

TRIGGER_COMMIT  = os.getenv("TRIGGER_COMMIT",  None)
TRIGGER_REPO    = os.getenv("TRIGGER_REPO",    None)
TRIGGER_ACTION  = os.getenv("TRIGGER_ACTION",  None)
DEPENDENT_BUILD = os.getenv("DEPENDENT_BUILD", None)

import dockerlief

PYTHON = shutil.which("python")


def build_doc(commit):
    main_script = (REPODIR / "dockerlief" / "main.py").as_posix()
    cmd = f"{PYTHON} {main_script} --debug build --branch={commit} lief-doc"

    logger.debug(f"Executing: {cmd}")

    kwargs = {
        'executable': '/bin/bash',
        'stdout':     subprocess.STDOUT,
        'stderr':     subprocess.STDOUT,
        'shell':      True,
        'cwd':        REPODIR,
    }
    p = subprocess.Popen(cmd, *kwargs)
    p.wait()

    if p.returncode:
        sys.exit(1)


def main(argv):

    if TRIGGER_ACTION == "build-doc":
        return build_doc(TRIGGER_COMMIT)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))


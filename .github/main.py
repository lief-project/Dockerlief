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
#sys.path.insert(0, REPODIR.as_posix())

TRIGGER_COMMIT  = os.getenv("TRIGGER_COMMIT",  None)
TRIGGER_REPO    = os.getenv("TRIGGER_REPO",    None)
TRIGGER_ACTION  = os.getenv("TRIGGER_ACTION",  None)
DEPENDENT_BUILD = os.getenv("DEPENDENT_BUILD", None)

DEPLOY_KEY = os.getenv("LIEF_AUTOMATIC_BUILDS_KEY", None)
DEPLOY_IV  = os.getenv("LIEF_AUTOMATIC_BUILDS_IV", None)

GIT_USER  = "Dockerlief"
GIT_EMAIL = "lief@quarkslab.com"

LIEF_WEBSITE_REPO = "https://github.com/lief-project/lief-project.github.io.git"

PYTHON = shutil.which("python")
GIT = shutil.which("git")

def setup_lief_website(branch="master"):
    cmd = f"{GIT} clone --branch=master --single-branch {LIEF_WEBSITE_REPO}"

    logger.debug(f"Executing: {cmd}")

    kwargs = {
        'shell':      True,
        'cwd':        REPODIR,
    }
    p = subprocess.Popen(cmd, **kwargs)
    p.wait()

    if p.returncode:
        sys.exit(1)

    cmds = [
        "chmod 700 .git",
        f"{GIT} config user.name '{GIT_USER}'",
        f"{GIT} config user.email '{GIT_EMAIL}'",
        f"{GIT} reset --soft HEAD~1",
        f"{GIT} ls-files -v",
    ]

    kwargs['cwd'] = REPODIR / "lief-project.github.io"
    for cmd in cmds:
        p = subprocess.Popen(cmd, **kwargs)
        p.wait()

        if p.returncode:
            sys.exit(1)




def build_doc(commit):
    main_script = (REPODIR / "dockerlief" / "main.py").as_posix()
    cmd = f"{PYTHON} {main_script} --debug build --branch={commit} lief-doc"

    logger.debug(f"Executing: {cmd}")

    kwargs = {
        #'stdout':     subprocess.STDOUT,
        #'stderr':     subprocess.STDOUT,
        'shell':      True,
        'cwd':        REPODIR,
    }
    p = subprocess.Popen(cmd, **kwargs)
    p.wait()

    if p.returncode:
        sys.exit(1)


def main(argv):

    if TRIGGER_ACTION == "build-doc":
        build_doc(TRIGGER_COMMIT)
        setup_lief_website()

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))


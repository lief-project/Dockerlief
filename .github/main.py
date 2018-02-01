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

LIEF_WEBSITE_REPO     = "https://github.com/lief-project/lief-project.github.io.git"
LIEF_WEBSITE_DIR      = REPODIR / "lief-project.github.io"
LIEF_WEBSITE_SSH_REPO = "git@github.com:lief-project/lief-project.github.io.git"

SSH_DIR = pathlib.Path("~/.ssh").resolve()


PYTHON  = shutil.which("python")
GIT     = shutil.which("git")
TAR     = shutil.which("tar")
OPENSSL = shutil.which("openssl")

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

    kwargs['cwd'] = LIEF_WEBSITE_DIR
    for cmd in cmds:
        p = subprocess.Popen(cmd, **kwargs)
        p.wait()

        if p.returncode:
            sys.exit(1)

    doc_archive = REPODIR / f"documentation-{TRIGGER_COMMIT}.tar.gz"

    cmds = [
        f"{TAR} -C {LIEF_WEBSITE_DIR}/doc/latest/ -xvf {doc_archive} doc/sphinx",
        f"{shutil.which('mv')} {LIEF_WEBSITE_DIR}/doc/latest/doc/sphinx/* -xvf {LIEF_WEBSITE_DIR}/doc/latest/",
        f"{GIT} add .",
        f"{GIT} diff --cached",
        f"{GIT} commit -m 'Update latest doc according to {TRIGGER_COMMIT[:7]}'"
        f"{GIT} ls-files -v"
        f"{GIT} log --pretty=fuller"
    ]

    for cmd in cmds:
        p = subprocess.Popen(cmd, **kwargs)
        p.wait()

        if p.returncode:
            sys.exit(1)

    setup_ssh()

    cmd = f"{GIT} push --force {LIEF_WEBSITE_SSH_REPO} 'master'"

    p = subprocess.Popen(cmd, **kwargs)
    p.wait()

    if p.returncode:
        sys.exit(1)


def fix_ssh_perms()
    SSH_DIR = pathlib.Path("~/.ssh").resolve().as_posix()
    cmd = f"chmod -c -R go-rwx {SSH_DIR}"

    p = subprocess.Popen(cmd, **kwargs)
    p.wait()

    if p.returncode:
        sys.exit(1)
    output_key_path.chmod(0o600)

def setup_ssh():
    if not SSH_DIR.is_dir():
        SSH_DIR.mkdir(mode=0o700)

    fix_ssh_perms()
    deploy_key_path = (REPODIR / ".github" / "deploy-key.enc").as_posix()
    output_key_path = (REPODIR / ".git" / "deploy-key")
    cmd = f"{OPENSSL} aes-256-cbc -K {DEPLOY_KEY} -iv {DEPLOY_IV} -in {deploy_key_path} -out {output_key_path.as_posix()} -d"

    kwargs = {
        'shell':      True,
        'cwd':        REPODIR,
    }

    p = subprocess.Popen(cmd, **kwargs)
    p.wait()

    if p.returncode:
        sys.exit(1)
    output_key_path.chmod(0o600)

    os.system(f"eval `ssh-agent -s`; ssh-add {output_key_path.as_posix()}")
    fix_ssh_perms()

    cmd = f"ssh-keyscan -H github.com >> {SSH_DIR}/known_hosts"

    kwargs = {
        'shell':      True,
        'cwd':        REPODIR,
    }

    p = subprocess.Popen(cmd, **kwargs)
    p.wait()

    if p.returncode:
        sys.exit(1)




def build_doc(commit):
    main_script = (REPODIR / "dockerlief" / "main.py").as_posix()
    cmd = f"{PYTHON} {main_script} --debug build --branch={commit} lief-doc"

    logger.debug(f"Executing: {cmd}")

    kwargs = {
        'shell':      True,
        'cwd':        REPODIR,
    }
    p = subprocess.Popen(cmd, **kwargs)
    p.wait()

    if p.returncode:
        sys.exit(1)

    setup_lief_website()


def main(argv):

    if TRIGGER_ACTION == "build-doc":
        build_doc(TRIGGER_COMMIT)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))


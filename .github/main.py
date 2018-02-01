#!/usr/bin/env python3.6
import sys
import os
import logging
import pathlib

CURRENTDIR = pathlib.Path(__file__).parent
sys.path.insert(0, CURRENTDIR.parent.as_posix())

TRIGGER_COMMIT  = os.getenv("TRIGGER_COMMIT",  None)
TRIGGER_REPO    = os.getenv("TRIGGER_REPO",    None)
TRIGGER_ACTION  = os.getenv("TRIGGER_ACTION",  None)
DEPENDENT_BUILD = os.getenv("DEPENDENT_BUILD", None)

import dockerlief


def main(argv):
    print(TRIGGER_COMMIT)
    print(TRIGGER_REPO)
    print(TRIGGER_ACTION)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))


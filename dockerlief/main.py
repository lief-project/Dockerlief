#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import colored
import argparse
import logging
import os
import docker
import sys
import traceback
from colored import stylize, fg
from functools import update_wrapper
from os.path import join, isfile

sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import dockerlief
from dockerlief import DockerAndroid, DockerCentos, DockerDoc, DockerFile, DockerDefault

BANNER = """
  ____             _               _     ___ _____ _____
 |  _ \  ___   ___| | _____ _ __  | |   |_ _| ____|  ___|
 | | | |/ _ \ / __| |/ / _ \ '__| | |    | ||  _| | |_
 | |_| | (_) | (__|   <  __/ |    | |___ | || |___|  _|
 |____/ \___/ \___|_|\_\___|_|    |_____|___|_____|_|

"""


logger = logging.getLogger(__name__)

dockerclient = docker.from_env()

# CLI Commands
class COMMANDS(object):
    HELP  = 0,
    BUILD = 1,
    LIST  = 2,


class exceptions_handler(object):
    func = None

    def __init__(self, exceptions, on_except_callback=None):
        self.exceptions         = exceptions
        self.on_except_callback = on_except_callback

    def __call__(self, *args, **kwargs):
        if self.func is None:
            self.func = args[0]
            update_wrapper(self, self.func)
            return self
        try:
            return self.func(*args, **kwargs)
        except self.exceptions as e:
            if self.on_except_callback is not None:
                self.on_except_callback(e)
            else:
                print("-" * 60)
                print("Exception in {}: {}".format(self.func.__name__, e))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback)
                print("-" * 60)




# ===========
#
# CLI Stuffs
#
# ===========

# Logging configuration
class ColoredFormatter(logging.Formatter):

    COLORS = {
        'DEBUG':    (colored.bg('grey_58')        + colored.fg('white'), colored.fg('deep_sky_blue_3b')),
        'INFO':     (colored.bg('dodger_blue_2')  + colored.fg('white'), colored.fg('dark_gray')),
        'WARNING':  (colored.bg('dark_orange_3a') + colored.fg('white'), colored.fg('orange_red_1')),
        'ERROR':    (colored.bg('deep_pink_2')    + colored.fg('white'), colored.fg('red_3b')),
        'CRITICAL': (colored.bg('red')            + colored.fg('white'), colored.fg('red_3b')),
    }

    def __init__(self, msg, **kwargs):
        super().__init__(msg, **kwargs)

    def format(self, record):
        levelname = record.levelname
        msg = record.msg

        if levelname in ColoredFormatter.COLORS:
            color_lvl, color_txt = ColoredFormatter.COLORS[levelname]
            reset = colored.attr('reset')

            levelname_color = color_lvl + levelname + reset
            msg_color = color_txt + msg + reset

            record.levelname = levelname_color
            record.msg = msg_color

        return logging.Formatter.format(self, record)


# Setup arguments for Verbosity
def init_verbosity_parser(parser):
    logger_group = parser.add_argument_group('Logger')
    verbosity = logger_group.add_mutually_exclusive_group()

    verbosity.add_argument('--debug',
            dest   = 'main_verbosity',
            action = 'store_const',
            const = logging.DEBUG)

    verbosity.add_argument('--info',
            action = 'store_const',
            dest   = 'main_verbosity',
            const  = logging.INFO)

    verbosity.add_argument('--warning',
            dest   = 'main_verbosity',
            action = 'store_const',
            const = logging.WARNING)

    verbosity.add_argument('--error',
            dest   = 'main_verbosity',
            action = 'store_const',
            const = logging.ERROR)

    verbosity.add_argument('--critical',
            dest   = 'main_verbosity',
            action = 'store_const',
            const = logging.CRITICAL)
    parser.set_defaults(main_verbosity = logging.INFO)


def build_subparser(sparser):
    build_subparser = sparser.add_parser('build', help="Build a LIEF Dockerfile")
    build_subparser.set_defaults(which=COMMANDS.BUILD)
    for docker in DockerFile:
        docker._setup_parser(build_subparser)


    build_subparser.add_argument('-b', '--branch',
            dest    = 'lief_branch',
            metavar = 'BRANCH',
            action  = 'store',
            help    = "Branch of LIEF to use (Default: '%(default)s')",
            default = "master")

    build_subparser.add_argument("tag")
    return build_subparser


def list_subparser(sparser):
    list_subparser = sparser.add_parser('list', help="List registred Dockerfile")
    list_subparser.set_defaults(which=COMMANDS.LIST)

    return list_subparser


def build_docker(args):
    logger.info("Building Dockerfile: '{}'".format(args.tag))
    dockerdir = args.docker_directory

    if not DockerFile.exists(args.tag):
        return logger.fatal("'{}' doesn't exists!".format(args.tag))


    dockerobject = DockerFile.get(args.tag)
    mydocker = dockerobject(args)
    mydocker(dockerclient)

def list_docker(args):
    for f in DockerFile:
        tag = f.TAG
        tag_color = fg("deep_sky_blue_1")
        if not isfile(join(args.docker_directory, f.FILE)):
            tag_color = fg("red")

        print("* {tag:30} {file:40}  {description}".format(
            tag=stylize(tag, tag_color),
            file=stylize(f.FILE,  fg("light_yellow")),
            description=stylize(f.DESCRIPTION, fg("dark_gray"))))


def setup_verbosity(args):
    root_logger = logging.getLogger()
    root_logger.setLevel(args.main_verbosity)

    ch = logging.StreamHandler()
    ch.setLevel(args.main_verbosity)

    FORMAT = '[{levelname:<5}] - {message:s}'
    color_formatter = ColoredFormatter(FORMAT, style = '{')
    ch.setFormatter(color_formatter)

    root_logger.addHandler(ch)

def main():
    print(stylize(BANNER, fg('dark_orange_3b')))

    parser = argparse.ArgumentParser(
            description="LIEF Docker manager",
            epilog="{name} - {version} - {license}".format(
                name=dockerlief.__name__.title(),
                version=dockerlief.__version__,
                license=dockerlief.__license__))
    parser.set_defaults(which=COMMANDS.HELP)

    parser.add_argument('-d', '--directory', '--dir',
            dest   = 'docker_directory',
            action = 'store',
            help   = "Location of the Dockerfiles (Default: %(default)s)",
            default = join(os.path.dirname(os.path.realpath(__file__)), 'dockerfiles'))

    init_verbosity_parser(parser)

    subparsers = parser.add_subparsers()
    build_subparser(subparsers)
    list_subparser(subparsers)

    args = parser.parse_args()

    setup_verbosity(args)

    logger.info("Location of the Dockerfiles: {}".format(args.docker_directory))

    if args.which == COMMANDS.BUILD:
        build_docker(args)

    if args.which == COMMANDS.LIST:
        list_docker(args)

    if args.which == COMMANDS.HELP:
        parser.print_help()



if __name__ == "__main__":
    main()

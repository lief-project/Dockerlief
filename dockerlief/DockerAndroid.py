#!/usr/bin/env python3
from colored import stylize, fg
import os
import json
import docker
import sys

from .DockerFile import DockerFile
class DockerAndroid(DockerFile):
    TAG  = "lief-android"
    FILE = "android.docker"
    DESCRIPTION = "Dockerfile used to build an Android version of LIEF"

    class ARCHITECTURES(object):
        X86_64  = 0
        X86     = 1
        ARM     = 2
        AARCH64 = 3

        ALL = [X86_64, X86, ARM, AARCH64]

    ARCH_TO_ABI = {
            ARCHITECTURES.X86_64  : 'x86_64',
            ARCHITECTURES.X86     : 'x86',
            ARCHITECTURES.ARM     : 'armeabi-v7a',
            ARCHITECTURES.AARCH64 : 'arm64-v8a',
        }

    def __init__(self, args=None):
        super().__init__(args)

    def _build(self, client, arch, api_level):
            abi = DockerAndroid.ARCH_TO_ABI[arch]
            self.LOGGER.info("Target architecture: {}".format(stylize(abi, fg("chartreuse_3a"))))
            self.LOGGER.info("Target API Level: {}".format(stylize(api_level, fg("chartreuse_3a"))))
            build_args = {
                'ANDROID_NATIVE_API_LEVEL' : str(api_level),
                'ANDROID_ABI': abi,
                'LIEF_BRANCH': self._args.lief_branch
            }
            self.LOGGER.debug("Build args: {!s}".format(build_args))

            client = docker.APIClient(base_url='unix://var/run/docker.sock')

            log = client.build(
                    path=self._args.docker_directory,
                    tag=DockerAndroid.TAG,
                    rm=False,
                    forcerm=False,
                    quiet=False,
                    buildargs=build_args,
                    dockerfile=DockerAndroid.FILE)

            for line in log:
                output = line.decode("utf8")
                output = output.strip('\r\n')
                json_output = json.loads(output)
                if 'stream' in json_output:
                    self.LOGGER.debug(json_output['stream'].strip('\n'))

            self.LOGGER.info("Image built!")

    def _run(self, client, arch, api_level):
        cmd = ["find",
            "/home/lief/LIEF-sources/LIEF/build",
            "-maxdepth", "1",
            "-name", "LIEF-*.tar.gz"
            ]
        container = client.containers.run(DockerAndroid.TAG, '/bin/bash', detach=True, stdin_open=True)
        package   = container.exec_run(cmd)
        package   = package.decode("utf-8").strip()
        output    = "LIEF-{tag}-Android_{arch}.tar.gz".format(tag=self._args.lief_branch, arch=DockerAndroid.ARCH_TO_ABI[arch])
        #output    = "{filename}_API{api:d}_{arch}.tar.gz".format(
        #        filename=os.path.basename(package).replace(".tar.gz", ""),
        #        api=api_level,
        #        arch=DockerAndroid.ARCH_TO_ABI[arch])

        self.LOGGER.info("Package '{package}' from '{tag!s}' will be downloaded at '{out}'".format(
            package=package,
            tag=DockerAndroid.TAG,
            out=output))
        try:
            raw, stat = container.get_archive(package)
            with open(output, 'wb') as f:
                f.write(raw.data)
        except docker.errors.NotFound as e:
            return self.LOGGER.error("Can't find '{}' in the Docker".format(package))
        except Exception as e:
            return self.LOGGER.error(e)

        self.LOGGER.info("Download done!")
        self.LOGGER.info("Shutting down the Docker...")
        container.stop()
        self.LOGGER.info("{tag!s} stopped!".format(tag=DockerAndroid.TAG))

    def process(self, client):
        dockerfile_path = os.path.join(self._args.docker_directory, DockerAndroid.FILE)

        if not os.path.isfile(dockerfile_path):
            return self.LOGGER.fatal("{} not found!".format(dockerfile_path))

        if self._args.architectures is None:
            self._args.architectures = DockerAndroid.ARCHITECTURES.ALL

        for arch in self._args.architectures:
            self._build(client, arch, self._args.api_level)
            self._run(client, arch, self._args.api_level)


    @staticmethod
    def _setup_parser(parser):
        parser.add_argument("--api-level", "--api",
            metavar = "API",
            help    = "API Level for the Android docker (Default: %(default)s)",
            dest    = "api_level",
            type    = int,
            action  ='store',
            default = 21)

        architecture_group = parser.add_argument_group('arch', description=
        """
        For Android docker, specify the target architecture
        """)

        architecture_group.add_argument('--x86-64',
                dest   = 'architectures',
                action = 'append_const',
                const  = DockerAndroid.ARCHITECTURES.X86_64)

        architecture_group.add_argument('--x86',
                dest   = 'architectures',
                action = 'append_const',
                const  = DockerAndroid.ARCHITECTURES.X86)

        architecture_group.add_argument('--arm',
                dest   = 'architectures',
                action = 'append_const',
                const  = DockerAndroid.ARCHITECTURES.ARM)

        architecture_group.add_argument('--aarch64',
                dest   = 'architectures',
                action = 'append_const',
                const  = DockerAndroid.ARCHITECTURES.AARCH64)

    def __del__(self):
        pass

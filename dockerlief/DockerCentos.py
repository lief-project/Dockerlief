#!/usr/bin/env python
import docker
import os

from .DockerFile import DockerFile

class DockerCentos(DockerFile):
    TAG  = "lief-centos"
    FILE = "centos.docker"
    DESCRIPTION = "Dockerfile used to compile LIEF for CentOS 7 - Python 3.5"

    def __init__(self, args=None):
        super().__init__(args)


    def _build(self, client):
        """
        Build the docker
        """
        dockerfile_path = os.path.join(self._args.docker_directory, DockerCentos.FILE)
        if not os.path.isfile(dockerfile_path):
            return self.LOGGER.fatal("{} not found!".format(dockerfile_path))

        client.images.build(
                path=self._args.docker_directory,
                tag=DockerCentos.TAG,
                rm=True,
                forcerm=True,
                quiet=False,
                dockerfile=DockerCentos.FILE)


    def _run(self, client):

        cmd = ["find",
            "/tmp/LIEF/LIEF/build",
            "-maxdepth", "1",
            "-name", "LIEF-*.tar.gz"
            ]
        container = client.containers.run(DockerCentos.TAG, '/usr/bin/bash', detach=True, stdin_open=True)
        package   = container.exec_run(cmd)
        package   = package.decode("utf-8").strip()
        output    = "{tag}_{filename}".format(tag=DockerCentos.TAG, filename=os.path.basename(package))

        self.LOGGER.info("Package '{package}' from '{tag!s}' will be downloaded at '{out}'".format(
            package=package,
            tag=DockerCentos.TAG,
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
        self.LOGGER.info("{tag!s} stopped!".format(tag=DockerCentos.TAG))

    @staticmethod
    def _setup_parser(parser):
        pass


    def __del__(self):
        pass

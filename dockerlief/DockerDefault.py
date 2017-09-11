#!/usr/bin/env python
import docker
import os

from .DockerFile import DockerFile

class DockerDefault(DockerFile):
    TAG  = "lief-default"
    FILE = "default.docker"
    DESCRIPTION = "Dockerfile to play with LIEF (Ubuntu 16.04 + Python 3.5)"

    def __init__(self, args=None):
        super().__init__(args)


    def _build(self, client):
        """
        Build the docker
        """
        dockerfile_path = os.path.join(self._args.docker_directory, DockerDefault.FILE)
        if not os.path.isfile(dockerfile_path):
            return self.LOGGER.fatal("{} not found!".format(dockerfile_path))

        self.LOGGER.info("Building the Docker...")
        client.images.build(
                path=self._args.docker_directory,
                tag=DockerDefault.TAG,
                rm=True,
                forcerm=True,
                quiet=False,
                dockerfile=DockerDefault.FILE)

        self.LOGGER.info("Build done!")


    def _run(self, client):
        print("You can now run 'docker run -it {tag}'".format(tag=DockerDefault.TAG))


    @staticmethod
    def _setup_parser(parser):
        pass


    def __del__(self):
        pass

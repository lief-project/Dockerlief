#!/usr/bin/env python3
import os
import docker
import json

from .DockerFile import DockerFile

class DockerDoc(DockerFile):
    TAG  = "lief-doc"
    FILE = "doc.docker"
    DESCRIPTION = "Dockerfile used to generate the LIEF documentation (Sphinx and Doxygen)"

    def __init__(self, args=None):
        super().__init__(args)

    def _build(self, client):
        """
        Build the docker
        """
        dockerfile_path = os.path.join(self._args.docker_directory, DockerDoc.FILE)
        if not os.path.isfile(dockerfile_path):
            return self.LOGGER.fatal("{} not found!".format(dockerfile_path))

        client = docker.APIClient(base_url='unix://var/run/docker.sock')

        build_args = {
            'LIEF_BRANCH': self._args.lief_branch
        }
        log = client.build(
                path=self._args.docker_directory,
                tag=DockerDoc.TAG,
                rm=False,
                forcerm=False,
                quiet=False,
                buildargs=build_args,
                dockerfile=DockerDoc.FILE)

        for line in log:
            output = line.decode("utf8")
            output = output.strip('\r\n')
            json_output = json.loads(output)
            if 'stream' in json_output:
                self.LOGGER.debug(json_output['stream'].strip('\n'))

        self.LOGGER.info("Image built!")


    def _run(self, client):
        container = client.containers.run(DockerDoc.TAG, detach=True)

        doc_path = "/tmp/LIEF_INSTALL/share/LIEF/doc"
        output = "documentation-{tag}.tar.gz".format(tag=self._args.lief_branch)
        try:
            raw, stat = container.get_archive(doc_path)
            with open(output, 'wb') as f:
                f.write(raw.data)
        except docker.errors.NotFound as e:
            return self.LOGGER.error("Can't find '{}' in the Docker".format(doc_path))
        except Exception as e:
            return self.LOGGER.error(e)

        self.LOGGER.info("Doc package has been downloaded here: {}".format(output))
        self.LOGGER.info("Shutting down the Docker...")
        container.stop()
        self.LOGGER.info("{tag!s} stopped!".format(tag=DockerDoc.TAG))

    @staticmethod
    def _setup_parser(parser):
        pass


    def __del__(self):
        pass

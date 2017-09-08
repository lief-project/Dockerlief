#!/usr/bin/env python

import logging

class MetaDocker(type):
    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)

        if not hasattr(cls, 'registry'):
            cls.registry = set()

        cls.registry.add(cls)
        cls.registry -= set(bases) # Remove base classes

        cls.name = cls.__name__

    def __iter__(cls):
        return iter(cls.registry)

class DockerFile(object, metaclass=MetaDocker):
    """
    Base class for all Docker object
    """
    TAG  = "lief-<unknown>"
    FILE = "unkwnown"
    DESCRIPTION = ""

    LOGGER = logging.getLogger(__name__)

    def __init__(self, args=None):
        self._logger = logging.getLogger(__name__)
        self._args   = args

    def _build(self, *args, **kwargs):
        raise NotImplementedError("This method should be overloaded")

    def _run(self, *args, **kwargs):
        raise NotImplementedError("This method should be overloaded")

    @staticmethod
    def get(tag):
        """
        Return a DockerFile given its tag
        """
        if not DockerFile.exists(tag):
            return DockerFile.LOGGER.fatal("Can't find a Docker object with tag '{}'".format(tag))
        return next(filter(lambda e : e.TAG == tag, DockerFile))

    @staticmethod
    def exists(tag):
        """
        Check if a DockerFile object with the given tag exists
        """
        try:
            next(filter(lambda e : e.TAG == tag, DockerFile))
            return True
        except StopIteration:
            return False

    @staticmethod
    def _setup_parser(parser):
        pass

    def __call__(self, client):
        self.process(client)

    def process(self, client):
        self._build(client)
        self._run(client)

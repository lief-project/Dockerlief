LIEF Docker files
=================

``dockerlief`` contains various Dockerfile as well as a *manager* to enjoy `LIEF <https://github.com/lief-project/LIEF>`_

To list all registered dockers:

.. code-block:: bash

  $ dockerlief list
  
.. image:: https://raw.githubusercontent.com/lief-project/Dockerlief/master/.github/img/list.png

To build and get the LIEF's documentation:

.. code-block:: bash

  $ dockerlief build lief-doc
  
.. image:: https://raw.githubusercontent.com/lief-project/Dockerlief/master/.github/img/build.png

Usage
-----

.. code-block:: bash

  dockerlief --help                                                                                                                                                                                                          (env: pylief)

    ____             _               _     ___ _____ _____
   |  _ \  ___   ___| | _____ _ __  | |   |_ _| ____|  ___|
   | | | |/ _ \ / __| |/ / _ \ '__| | |    | ||  _| | |_
   | |_| | (_) | (__|   <  __/ |    | |___ | || |___|  _|
   |____/ \___/ \___|_|\_\___|_|    |_____|___|_____|_|


  usage: dockerlief [-h] [-d DOCKER_DIRECTORY]
                    [--debug | --info | --warning | --error | --critical]
                    {build,list} ...

  LIEF Docker manager

  positional arguments:
    {build,list}
      build               Build a LIEF Dockerfile
      list                List registred Dockerfile

  optional arguments:
    -h, --help            show this help message and exit
    -d DOCKER_DIRECTORY, --directory DOCKER_DIRECTORY, --dir DOCKER_DIRECTORY
                          Location of the Dockerfiles (Default:
                          INSTALL_PATH/dockerlief/dockerfiles)

  Logger:
    --debug
    --info
    --warning
    --error
    --critical

  Dockerlief - 0.1.0 - Apache 2.0



To run a Dockerfile manually:

.. code-block:: bash

  $ docker build -f DOCKERFILE_PATH -t DOCKER_TAG .
  $ docker run -i -t DOCKER_TAG /bin/bash



Android Docker
--------------

The Dockerfile ``android.docker`` is used to compile LIEF for Android

You can specify the target architecture / api level as follow:

.. code-block:: bash

  $ dockerlief build --api-level 21 --arm lief-android



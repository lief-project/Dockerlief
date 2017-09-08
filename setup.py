#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
current_directory = os.path.abspath(os.path.dirname(__file__))

requirements = ['colored==1.3.3', 'docker==2.5.1']
entry_points={
        'console_scripts': [
            "dockerlief=dockerlief.main:main",
        ]
}

information = {}
with open(os.path.join(current_directory, 'dockerlief', '__about__.py'), 'r') as f:
    exec(f.read(), information)

package_description = '''
Dockerfiles to build and use LIEF
'''.strip()

setup(
    name                 = information['__title__'],
    version              = information['__version__'],
    license              = information['__license__'],
    description          = package_description,
    url                  = 'http://lief.quarkslab.com',
    author               = information['__author__'],
    author_email         = information['__author_email__'],
    packages             = find_packages(),
    package_data         = {'': ['*.docker']},
    include_package_data = True,
    install_requires     = requirements,
    zip_safe             = True,
    entry_points         = entry_points,
    classifiers          = [
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
	'Intended Audience :: Science/Research',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Windows :: Windows',
        'Programming Language :: C++',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Security',
        'Topic :: Scientific/Engineering :: Information Analysis',
	'Topic :: Software Development :: Build Tools',
    ],
)

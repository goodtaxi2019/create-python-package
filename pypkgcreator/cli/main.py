#!/usr/bin/env python
"""
Python package scaffold builder

Usage:
    create-python-package -h|--help
    create-python-package -v|--version
    create-python-package [--debug|--info] [--docker] [--module=<name>] <path>

Options:
    -h, --help          Print help and exit
    -v, --version       Print version and exit
    --debug, --info     Execute a command with debug|info messages
    --docker            Create Dockerfile and docker-compose.yml
    --static            Include static fileas
    --module=<name>     Specify a module name

Arguments:
    <path>              Path to a directory for a new project directory
"""

import logging
import os
import re
from pathlib import PurePath

from docopt import docopt

from .. import __version__


def main():
    args = docopt(
        __doc__, version='create-python-package {}'.format(__version__)
    )
    _set_log_config(debug=args['--debug'], info=args['--info'])
    logger = logging.getLogger(__name__)
    logger.debug('args:{0}{1}'.format(os.linesep, args))
    create_python_package_scaffold(args=args)


def _set_log_config(debug=None, info=None):
    if debug:
        lv = logging.DEBUG
    elif info:
        lv = logging.INFO
    else:
        lv = logging.WARNING
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S', level=lv
    )


def create_python_package_scaffold(args):
    project_path = PurePath(args['<path>'])
    module_name = re.sub(
        r'[\.\-]', '_', (args['--module'] or project_path.name)
    )

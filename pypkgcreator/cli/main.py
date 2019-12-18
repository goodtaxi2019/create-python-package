#!/usr/bin/env python
"""
Python package scaffold builder

Usage:
    create-python-package -h|--help
    create-python-package -v|--version
    create-python-package [--debug|--info] [--module=<name>] <path>

Options:
    -h, --help          Print help and exit
    -v, --version       Print version and exit
    --debug, --info     Execute a command with debug|info messages
    --module=<name>     Specify a module name

Arguments:
    <path>              Path to a directory for a new project directory
"""

import logging
import os
import re
from pathlib import PurePath

from docopt import docopt
from jinja2 import Environment, FileSystemLoader

from .. import __version__


def main():
    args = docopt(
        __doc__, version='create-python-package {}'.format(__version__)
    )
    _set_log_config(debug=args['--debug'], info=args['--info'])
    logger = logging.getLogger(__name__)
    logger.debug('args:{0}{1}'.format(os.linesep, args))
    _create_python_package_scaffold(args=args)


def _create_python_package_scaffold(args, include_package_data=True,
                                    create_dockerfile=True):
    project_path = PurePath(args['<path>'])
    package_name = args['--module'] or project_path.name
    package_path = project_path.joinpath(re.sub(r'[\.\-]', '_', package_name))
    package_path.mkdir(exist_ok=True)
    data = {
        'package_name': package_name, 'module_name': package_path.name,
        'include_package_data': str(include_package_data),
        'version': 'v0.0.1', 'description': '', 'user_name': '', 'url': ''
    }


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


def _render_j2_template(data, j2_template, output_path):
    with open(output_path, 'w') as f:
        f.write(
            Environment(
                loader=FileSystemLoader(
                    PurePath(__file__).parents[1].joinpath('template'),
                    encoding='utf8'
                )
            ).get_template(j2_template).render(data).encode('utf-8')
        )

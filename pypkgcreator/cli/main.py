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
    <path>              Path to a directory for a new repository directory
"""

import logging
import os
import re
from configparser import ConfigParser
from pathlib import Path, PurePath

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
    repo_path = PurePath(args['<path>'])
    package_name = args['--module'] or repo_path.name
    package_path = repo_path.joinpath(re.sub(r'[\.\-]', '_', package_name))
    package_path.mkdir(exist_ok=True)
    data = {
        'package_name': package_name, 'module_name': package_path.name,
        'include_package_data': str(include_package_data),
        'version': 'v0.0.1', 'description': '',
        **_fetch_git_config(repo_path=str(repo_path))
    }
    return data


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


def _fetch_git_config(repo_path):
    local_gitconfig = Path(repo_path).joinpath('.git/config')
    local_cf = (
        _read_config_file(path=str(local_gitconfig))
        if local_gitconfig.exists else dict()
    )
    global_gitconfig = Path.home().joinpath('.gitconfig')
    global_cf = (
        _read_config_file(path=str(global_gitconfig))
        if global_gitconfig.exists else dict()
    )
    if local_cf.get('user'):
        author = str(local_cf['user'].get('name'))
        author_email = str(local_cf['user'].get('email'))
    elif global_cf.get('user'):
        author = str(global_cf['user'].get('name'))
        author_email = str(global_cf['user'].get('email'))
    else:
        author = ''
        author_email = ''
    if local_cf.get('remote "origin"'):
        url = str(local_cf['remote "origin"'].get('url'))
        user_name = re.split(r'[:/]', url)[-2] if url and '/' in url else ''
    else:
        url = ''
        user_name = ''
    return {
        'author': author, 'author_email': author_email, 'url': url,
        'user_name': user_name
    }


def _read_config_file(path):
    c = ConfigParser()
    c.read(path)
    return {k: dict(v) for k, v in c.items()}


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

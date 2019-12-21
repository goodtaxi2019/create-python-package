#!/usr/bin/env python

import logging
import re
import shutil
from configparser import ConfigParser
from pathlib import Path, PurePath

from jinja2 import Environment, FileSystemLoader


def set_log_config(debug=None, info=None):
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


def fetch_description_from_readme(md_path):
    short_description = ''
    with open(md_path, 'r') as f:
        for i, r in enumerate(f):
            if i > 0 and r.strip() and not r.startswith(('#', '=', '-')):
                short_description = r.strip()
                break
    return short_description


def fetch_git_config(repo_path):
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


def render_template(output_path, data=None, template=None):
    logger = logging.getLogger(__name__)
    if Path(output_path).exists:
        logger.info('Skip rendering a file:\t{}'.format(output_path))
    else:
        _print_log('Render a file:\t{}'.format(output_path))
        if data is not None:
            with open(output_path, 'w') as f:
                f.write(
                    Environment(
                        loader=FileSystemLoader(
                            str(PurePath(__file__).joinpath('../template')),
                            encoding='utf8'
                        )
                    ).get_template(
                        template or (PurePath(output_path).name + '.j2')
                    ).render(data).encode('utf-8')
                )
        else:
            shutil.copyfile(
                str(
                    PurePath(__file__).joinpath('../static').joinpath(
                        template or PurePath(output_path).name
                    )
                ),
                output_path
            )


def _print_log(message):
    logger = logging.getLogger(__name__)
    logger.info(message)
    print('>>\t{}'.format(message), flush=True)

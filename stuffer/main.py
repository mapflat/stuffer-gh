import logging
import os

from stuffer import content
from stuffer import debconf


os.environ['LANG'] = 'C.UTF-8'
os.environ['LC_ALL'] = 'C.UTF-8'

import click
import click_config
import sys

from . import apt
from . import configuration
from . import contrib
from . import files
from . import pip
from . import store
from . import user
from .core import Action


def command_script(file_path, operations):
    if operations:
        if file_path:
            raise click.UsageError("Cannot pass both --file/-f and operations on command line")
        return "\n".join(operations) + "\n"
    logging.info("Reading commands from %s", file_path)
    with open(file_path) as f:
        contents = f.read()
        logging.info("Read %d bytes from %s", len(contents), file_path)
        return contents


def script_substance(contents):
    all_lines = contents.splitlines()
    no_comments = [line for line in all_lines if not line.startswith('#')]
    return "\n".join([line for line in no_comments if line.strip()] + [''])


@click.command()
@click_config.wrap(module=configuration.config, sections=["store"])
@click.option("--file", "-f", 'file_path')
@click.argument("operations", nargs=-1)
def cli(file_path, operations):
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S')
    script = command_script(file_path, operations)
    logging.debug("Read script:\n%s", script)
    full_command = script_substance(script)
    logging.debug("Script substance:\n%s", full_command)
    action_namespace = {'apt': apt, 'configuration': configuration, 'content': content, 'contrib': contrib,
                        'debconf': debconf, 'files': files, 'pip': pip, 'store': store, 'user': user}
    if not Action.tmp_dir().is_dir():
        Action.tmp_dir().mkdir(parents=True)
    exec(full_command, action_namespace)

    actions = list(Action.registered())
    logging.info("Loaded %d actions: %s", len(actions), ', '.join(map(repr, actions)))
    for act in actions:
        act.execute()

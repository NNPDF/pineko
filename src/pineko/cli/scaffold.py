"""'scaffold' mode of CLI."""
import pathlib

import click

from .. import configs, scaffold
from ._base import command


@command.group("scaffold")
@click.option(
    "-c",
    "--configs",
    "cfg",
    default=None,
    type=click.Path(resolve_path=True, path_type=pathlib.Path),
    help="Explicitly specify config file (it has to be a valid TOML file).",
)
def scaffold_(cfg):
    """Set the configs."""
    path = configs.detect(cfg)
    base_configs = configs.load(path)
    configs.configs = configs.defaults(base_configs)
    if cfg is not None:
        print(f"Configurations loaded from '{path}'")


@scaffold_.command()
def new():
    """Create all the folders to set up a new project."""
    scaffold.set_up_project(configs.configs)

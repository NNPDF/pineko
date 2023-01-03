"""'scaffold' mode of CLI."""
import pathlib

import click
import rich

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
    """Manage folders needed for the project as spelled out in the configuration file."""
    path = configs.detect(cfg)
    base_configs = configs.load(path)
    configs.configs = configs.defaults(base_configs)
    if cfg is not None:
        print(f"Configurations loaded from '{path}'")


@scaffold_.command()
def new():
    """Create all the folders to set up a new project."""
    scaffold.set_up_project(configs.configs)


@scaffold_.command()
def check():
    """Check if all the configurations are correct."""
    success, wrong_confs, wrong_folders = scaffold.check_folders(configs.configs)
    if success:
        rich.print("[green]Success:[/] All the folders are correctly configured.")
    else:
        rich.print("[red]Error:[/] Project is not correctly configured.")
        for conf in wrong_confs:
            rich.print(f"[red]Missing entry in conf file: '{conf}'")
        for key in wrong_folders:
            if not isinstance(wrong_folders[key], dict):
                rich.print(f"[red]Missing folder: \t{wrong_folders[key]}")
            else:
                for log_key in wrong_folders[key]:
                    rich.print(f"[red]Missing folder: \t{wrong_folders[key][log_key]}")

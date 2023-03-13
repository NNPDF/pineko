"""CLI entry point to generation of the inclusion of kfactor in a grid."""

import pathlib

import click
import pineappl
import rich

from .. import kfactor_inclusion
from ._base import command


@command.command("k_factor_inclusion")
@click.argument("grids_folder", type=click.Path(exists=True))
@click.argument("kfactor_folder", type=click.Path(exists=True))
@click.argument("yamldb_path", type=click.Path(exists=True))
@click.argument("target_folder", type=click.Path(exists=False))
@click.argument("max_as", type=int)
@click.option(
    "--comp",
    default=None,
    type=click.Path(exists=True),
    help="path to compound file if exists",
)
def k_factor_inclusion(
    grids_folder, kfactor_folder, yamldb_path, target_folder, max_as, comp
):
    """Construct new grid with k_factor included."""
    grids_folder = pathlib.Path(grids_folder)
    kfactor_folder = pathlib.Path(kfactor_folder)
    yamldb_path = pathlib.Path(yamldb_path)
    target_folder = pathlib.Path(target_folder)
    if comp is not None:
        comp = pathlib.Path(comp)
    kfactor_inclusion.compute_k_factor_grid(
        grids_folder,
        kfactor_folder,
        yamldb_path,
        comp,
        max_as,
        target_folder=target_folder,
    )

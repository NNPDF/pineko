"""CLI entry point to generation of the inclusion of kfactor in a grid."""

import pathlib

import click
import pineappl
import rich

from .. import kfactor
from ._base import command


@command.command("kfactor")
@click.argument("grids_folder", type=click.Path(exists=True))
@click.argument("kfactor_folder", type=click.Path(exists=True))
@click.argument("yamldb_path", type=click.Path(exists=True))
@click.argument("compound_folder", type=click.Path(exists=True))
@click.argument("target_folder", type=click.Path(exists=False))
@click.argument("max_as", type=int)
def k_factor_inclusion(
    grids_folder,
    kfactor_folder,
    yamldb_path,
    compound_folder,
    target_folder,
    max_as,
):
    """Construct new grid with k_factor included."""
    kfactor.compute_k_factor_grid(
        grids_folder,
        kfactor_folder,
        yamldb_path,
        compound_folder,
        max_as,
        target_folder=target_folder,
    )

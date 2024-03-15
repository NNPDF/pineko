"""CLI entry point to generation of the inclusion of kfactor in a grid."""

import pathlib

import click

from .. import kfactor
from ._base import command


@command.command("kfactor")
@click.argument("grids_folder", type=click.Path(exists=True))
@click.argument("kfactor_folder", type=click.Path(exists=True))
@click.argument("yamldb_path", type=click.Path(exists=True))
@click.argument("target_folder", type=click.Path(exists=True))
@click.argument("order_to_update", type=int)
@click.argument("order_exists", type=bool)
def k_factor_inclusion(
    grids_folder,
    kfactor_folder,
    yamldb_path,
    target_folder,
    order_to_update,
    order_exists,
):
    """Construct new grid with k_factor included.

    parameters
    ----------
    grids_folder:
        path to grids folder
    kfactor_folder:
        path to kfactor folder.
    yamldb_path:
        path to yamldb file.
    target_folder:
        path to updated grids folder.
    order_to_update:
        alpha_s order to update.
    order_exists:
        True if the order is already present.

    """
    grids_folder = pathlib.Path(grids_folder)
    kfactor_folder = pathlib.Path(kfactor_folder)
    yamldb_path = pathlib.Path(yamldb_path)
    target_folder = pathlib.Path(target_folder)
    kfactor.compute_k_factor_grid(
        grids_folder,
        kfactor_folder,
        yamldb_path,
        order_to_update,
        target_folder=target_folder,
        order_exists=order_exists,
    )

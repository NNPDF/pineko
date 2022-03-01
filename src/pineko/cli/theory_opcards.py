# -*- coding: utf-8 -*-
import click
import rich

from .. import parser, configs, evolve
from ._base import command


@command.command("theory_opcards")
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
def subcommand(theory_id, datasets):
    """Write EKO card for all FK tables in all datasets."""
    paths = configs.configs.paths
    for ds in datasets:
        rich.print(f"Analyze {ds}")
        try:
            _info, grids = parser.get_yaml_information(paths.ymldb / f"{ds}.yaml", paths.grids / str(theory_id))
        except FileNotFoundError:
            _info, grids = parser.get_yaml_information(paths.ymldb / f"{ds}.yaml", paths.grids_common)
        # the list is still nested, so flatten
        grids = [grid for opgrids in grids for grid in opgrids]
        for grid in grids:
            name = grid.stem.rsplit(".",1)[0]
            opcard_path = paths.opcards / f"{name}.yaml"
            x_grid, q2_grid = evolve.write_operator_card_from_file(grid, paths.opcard_template,opcard_path)
            rich.print(f"[green]Success:[/] Wrote card with {len(q2_grid)} Q2 points to {opcard_path}")
        print()

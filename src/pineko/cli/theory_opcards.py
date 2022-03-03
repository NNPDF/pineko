# -*- coding: utf-8 -*-
import click
import rich

from .. import configs, evolve, parser
from ._base import command


@command.command("theory_opcards")
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
def subcommand(theory_id, datasets):
    """Write EKO card for all FK tables in all datasets."""
    paths = configs.configs["paths"]
    for ds in datasets:
        rich.print(f"Analyze {ds}")
        grids = parser.load_grids(theory_id, ds)
        for name, grid in grids.items():
            opcard_path = paths["operator_cards"] / f"{name}.yaml"
            _x_grid, q2_grid = evolve.write_operator_card_from_file(
                grid, paths["opcard_template"], opcard_path
            )
            rich.print(
                f"[green]Success:[/] Wrote card with {len(q2_grid)} Q2 points to {opcard_path}"
            )
        print()

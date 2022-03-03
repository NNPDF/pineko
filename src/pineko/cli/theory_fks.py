# -*- coding: utf-8 -*-
import click
import rich

from .. import configs, evolve, parser, theory_card
from ._base import command


@command.command("theory_fks")
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--logs", is_flag=True, help="dump logs")
def subcommand(theory_id, datasets, logs):
    """Compute FK tables in all datasets."""
    # setup data
    paths = configs.configs["paths"]
    tcard = theory_card.load(theory_id)
    eko_path = paths["ekos"] / str(theory_id)
    fk_path = paths["fktables"] / str(theory_id)
    fk_path.mkdir(exist_ok=True)
    # iterate datasets
    for ds in datasets:
        rich.print(f"Analyze {ds}")
        # iterate grids
        grids = parser.load_grids(theory_id, ds)
        for name, grid in grids.items():
            eko_filename = eko_path / f"{name}.tar"
            fk_filename = fk_path / f"{ds}-{name}.{parser.ext}"
            # activate logging
            # if logs and paths["logs"]["eko"]:
            evolve.evolve_grid(
                grid, eko_filename, fk_filename, 1 + int(tcard["PTO"]), 0
            )
            # do it!
            rich.print(f"[green]Success:[/] Wrote FK table to {fk_filename}")
        print()

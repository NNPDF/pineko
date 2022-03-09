# -*- coding: utf-8 -*-
import click
import rich

from .. import comparator, configs, evolve, parser, theory_card
from ._base import command


@command.command("theory_fks")
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--logs", is_flag=True, help="dump comparison")
@click.option("--pdf", "-p", default=None, help="comparison PDF")
def subcommand(theory_id, datasets, logs, pdf):
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
        for name, grid_path in grids.items():
            eko_filename = eko_path / f"{name}.tar"
            fk_filename = fk_path / f"{name}.{parser.ext}"
            max_as = 1 + int(tcard["PTO"])
            max_al = 0
            # do it!
            _grid, _fk, comparison = evolve.evolve_grid(
                grid_path, eko_filename, fk_filename, max_as, max_al, pdf
            )
            # activate logging
            if logs and paths["logs"]["fk"] and comparison:
                logfile = paths["logs"]["fk"] / f"{theory_id}-{name}-{pdf}.log"
                logfile.write_text(comparison.to_string())
            rich.print(f"[green]Success:[/] Wrote FK table to {fk_filename}")
        print()

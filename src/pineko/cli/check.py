# -*- coding: utf-8 -*-
import click
import rich

from .. import check
from ._base import command


@command.command("check")
@click.argument("pineappl", type=click.Path(exists=True))
@click.argument("eko", type=click.Path(exists=True))
def subcommand(pineappl, eko):
    """Check PineAPPL grid and EKO compatibility.

    In order to be compatible, the grid provided in PINEAPPL and the operator
    provided in EKO, have to expose the same: x grid, Q2 grid.
    """
    pineappl_grid = pineappl.grid.Grid.read(pineappl)
    operators = eko.output.Output.load_yaml_from_file(eko)
    try:
        check.check_grid_and_eko_compatible(pineappl_grid, operators)
        rich.print("[green]Success:[/] grids are compatible")
    except ValueError as e:
        rich.print("[red]Error:[/]", e)

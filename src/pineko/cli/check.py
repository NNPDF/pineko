# -*- coding: utf-8 -*-
"""CLI entry point to check compatibility."""
import click
import eko.output
import pineappl
import rich

from .. import check
from ._base import command


@command.group("check")
def subcommand():
    """Check grid and operator properties."""


@subcommand.command("compatibility")
@click.argument("grid_path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument("operator_path", metavar="EKO", type=click.Path(exists=True))
@click.option("--xif", default=1.0, help="factorization scale variation")
def sub_compatibility(grid_path, operator_path, xif):
    """Check PineAPPL grid and EKO compatibility.

    In order to be compatible, the grid provided in PINEAPPL and the operator
    provided in EKO, have to expose the same x grid and Q2 grid.

    XIF is the factorization scale variation.

    """
    pineappl_grid = pineappl.grid.Grid.read(grid_path)
    operators = eko.output.Output.load_tar(operator_path)
    try:
        check.check_grid_and_eko_compatible(pineappl_grid, operators, xif)
        rich.print("[green]Success:[/] grids are compatible")
    except ValueError as e:
        rich.print("[red]Error:[/]", e)


@subcommand.command("scvar")
@click.argument("grid_path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument(
    "scale",
    metavar="SCALE",
    type=click.Choice(["ren", "fact"]),
)
@click.argument("max_as_order", metavar="AS_ORDER", type=int)
@click.argument("max_al_order", metavar="AL_ORDER", type=int)
def sub_scvar(grid_path, scale, max_as_order, max_al_order):
    """Check if PineAPPL grid contains requested scale variations for the requested order."""
    grid = pineappl.grid.Grid.read(grid_path)
    grid.optimize()
    if scale == "ren":
        is_ren_as, is_ren_al = check.contains_ren(grid, max_as_order, max_al_order)
        if is_ren_as:
            rich.print(
                "[green]Success:[/] grids contain renormalization scale variations for as"
            )
        else:
            rich.print(
                "[red]Error:[/] grids do not contain renormalization scale variations for as"
            )
        if is_ren_al:
            rich.print(
                "[green]Success:[/] grids contain renormalization scale variations for al"
            )
        else:
            rich.print(
                "[red]Error:[/] grids do not contain renormalization scale variations for al"
            )
    elif scale == "fact":
        is_fact_as, is_fact_al = check.contains_fact(grid, max_as_order, max_al_order)
        if is_fact_as:
            rich.print(
                "[green]Success:[/] grids contain factorization scale variations for as"
            )
        else:
            rich.print(
                "[red]Error:[/] grids do not contain factorization scale variations for as"
            )
        if is_fact_al:
            rich.print(
                "[green]Success:[/] grids contain factorization scale variations for al"
            )
        else:
            rich.print(
                "[red]Error:[/] grids do not contain factorization scale variations for al"
            )
    else:
        raise ValueError("Scale variation to check can be one between xir and xif")

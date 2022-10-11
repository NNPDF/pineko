# -*- coding: utf-8 -*-
"""CLI entry point to check compatibility."""
from enum import Enum, auto

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


class Scale(Enum):
    """Auxiliary class to list the possible scale variations."""

    REN = auto()
    FACT = auto()


@subcommand.command("scvar")
@click.argument("grid_path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument(
    "scale",
    metavar="SCALE",
    type=click.Choice(list(map(lambda x: x.name.upper(), Scale)), case_sensitive=False),
)
@click.argument("max_as_order", metavar="AS_ORDER", type=int)
@click.argument("max_al_order", metavar="AL_ORDER", type=int)
def sub_scvar(grid_path, scale, max_as_order, max_al_order):
    """Check if PineAPPL grid contains requested scale variations for the requested order."""
    grid = pineappl.grid.Grid.read(grid_path)
    grid.optimize()
    success = "[green]Success:[/] grids contain"
    error = "[red]Error:[/] grids do not contain"
    scale_variations = {
        Scale.REN.name: " renormalization scale variations",
        Scale.FACT.name: " factorization scale variations",
    }
    if scale not in scale_variations.keys():
        raise ValueError("Scale variation to check can be one between ren and fact")
    sv = scale_variations[scale]
    funcs = {Scale.REN.name: check.contains_ren, Scale.FACT.name: check.contains_fact}
    func_to_call = funcs[scale]
    # Call the function
    is_sv_as, is_sv_al = func_to_call(grid, max_as_order, max_al_order)
    conditions = {" for as": is_sv_as, " for al": is_sv_al}
    for cond in conditions.keys():
        to_write = ""
        if conditions[cond]:
            to_write += success
        else:
            to_write += error
        to_write += sv
        to_write += cond
        rich.print(to_write)

"""CLI entry point to convolution."""
import click
import eko
import pineappl
import rich

from .. import evolve
from ._base import command


@command.command("convolute")
@click.argument("grid_path", type=click.Path(exists=True))
@click.argument("op_path", type=click.Path(exists=True))
@click.argument("fktable", type=click.Path())
@click.argument("max_as", type=int)
@click.argument("max_al", type=int)
@click.option("--xir", default=1.0, help="renormalization scale variation")
@click.option("--xif", default=1.0, help="factorization scale variation")
@click.option(
    "--pdf", default=None, help="if given, print comparison table", show_default=True
)
@click.option(
    "--assumptions",
    default="Nf6Ind",
    help="the flavor assumptions to be used",
    show_default=True,
)
def subcommand(grid_path, op_path, fktable, max_as, max_al, xir, xif, pdf, assumptions):
    """Convolute PineAPPL grid and EKO into an FK table.

    GRID_PATH and OP_PATH are the path to the respective elements to convolute, and
    FKTABLE is the path where to dump the output.

    MAX_AS and MAX_AL are used to specify the order in QCD and QED
    couplings (i.e. the maximum power allowed for each correction).

    XIR and XIF represent the renormalization and factorization scale in the grid respectively.

    ASSUMPTIONS represent the assumptions on the flavor dimension.

    PDF is an optional PDF set compatible with the EKO to compare grid and FK table.
    """
    grid = pineappl.grid.Grid.read(grid_path)
    with eko.EKO.edit(op_path) as operators:
        rich.print(
            rich.panel.Panel.fit("Computing ...", style="magenta", box=rich.box.SQUARE),
            f"   {grid_path}\n",
            f"+ {op_path}\n",
            f"= {fktable}\n",
            f"with max_as={max_as}, max_al={max_al}, xir={xir}, xif={xif}",
        )
        _grid, _fk, comp = evolve.evolve_grid(
            grid,
            operators,
            fktable,
            max_as,
            max_al,
            xir,
            xif,
            assumptions=assumptions,
            comparison_pdf=pdf,
        )
        if comp:
            print(comp.to_string())

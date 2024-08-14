"""CLI entry point to convolution."""

import click
import eko
import pineappl
import rich

from .. import evolve
from ._base import command


@command.command("convolve")
@click.argument("fktable", type=click.Path())
@click.argument("grid_path", type=click.Path(exists=True))
@click.argument("max_as", type=int)
@click.argument("max_al", type=int)
@click.argument("op_paths", type=click.Path(exists=True), nargs=-1)
@click.option("--xir", default=1.0, help="renormalization scale variation")
@click.option("--xif", default=1.0, help="factorization scale variation")
@click.option("--min_as", type=int, help="Minimum exponent of as")
@click.option(
    "--pdf1",
    default=None,
    help="PDF for the first convolution. If given, print comparison table",
    show_default=True,
)
@click.option(
    "--pdf2", default=None, help="PDF for the second convolution.", show_default=True
)
@click.option(
    "--assumptions",
    default="Nf6Ind",
    help="the flavor assumptions to be used",
    show_default=True,
)
def subcommand(
    fktable,
    grid_path,
    max_as,
    max_al,
    op_paths,
    xir,
    xif,
    pdf1,
    pdf2,
    assumptions,
    min_as,
):
    """Convolute PineAPPL grid and EKO into an FK table.

    GRID_PATH and OP_PATH are the path to the respective elements to convolve.
    Note that multiple operators are allowed.
    FKTABLE is the path where to dump the output.

    MAX_AS and MAX_AL are used to specify the order in QCD and QED
    couplings (i.e. the maximum power allowed for each correction)
    e.g., max_as = 1, max_al = 0 would select LO QCD only
    max_as = 3 instead would select LO, NLO, NNLO QCD.
    While, by default, all orders below MAX_AS will be selected, it is also possible
    to selected only from a certain order. E.g., to get only NNLO & NLO contributions
    it is possible to set max_as = 3, min_as = 2

    XIR and XIF represent the renormalization and factorization scale in the grid respectively.

    ASSUMPTIONS represent the assumptions on the flavor dimension.

    PDF is an optional PDF set compatible with the EKO to compare grid and FK table.
    """
    grid = pineappl.grid.Grid.read(grid_path)
    n_ekos = len(op_paths)
    with eko.EKO.edit(op_paths[0]) as operators1:
        rich.print(
            rich.panel.Panel.fit("Computing ...", style="magenta", box=rich.box.SQUARE),
            f"   {grid_path}\n",
            f"+ {op_paths[0]}\n",
            f"+ {op_paths[1]}\n" if n_ekos > 1 else "",
            f"= {fktable}\n",
            f"with max_as={max_as}, max_al={max_al}, xir={xir}, xif={xif}",
            f"min_as: {min_as}" if min_as is not None else "",
        )
        if n_ekos == 2:
            operators2 = eko.EKO.edit(op_paths[1])
        else:
            operators2 = None

        _grid, _fk, comp = evolve.evolve_grid(
            grid,
            operators1,
            fktable,
            max_as,
            max_al,
            xir,
            xif,
            operators2=operators2,
            assumptions=assumptions,
            comparison_pdf1=pdf1,
            comparison_pdf2=pdf2,
            min_as=min_as,
        )

        if n_ekos == 2:
            operators2.close()

        if comp is not None:
            print(comp.to_string())

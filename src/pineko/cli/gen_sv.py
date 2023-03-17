"""CLI entry point to generation of scale variations from central grid."""

import click
import pineappl
import rich

from .. import scale_variations
from ._base import command


@command.command("ren_sv_grid")
@click.argument("pineappl_path", type=click.Path(exists=True))
@click.argument("target_path", type=click.Path(exists=False))
@click.argument("max_as", type=int)
@click.argument("nf", type=int)
def ren_sv_grid(pineappl_path, target_path, max_as, nf):
    """Construct new grid with renormalization scale variations included."""
    scale_variations.compute_ren_sv_grid(
        pineappl_path, max_as, nf, target_path=target_path
    )
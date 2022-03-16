# -*- coding: utf-8 -*-
import click

from .. import theory
from ._base import command


@command.group("theory")
def theory_():
    """Iterate a subcommand on a given theory and list of datasets"""


@theory_.command()
@click.argument("source_theory_id", type=click.INT)
@click.argument("target_theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
def inherit_grids(source_theory_id, target_theory_id, datasets):
    """Inherit grids from one theory to another."""
    theory.TheoryBuilder(source_theory_id, datasets).inherit_grids(target_theory_id)

@theory_.command()
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
def opcards(theory_id, datasets, overwrite):
    """Write EKO card for all FK tables in all datasets."""
    theory.TheoryBuilder(theory_id, datasets, overwrite).opcards()


@theory_.command()
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--logs", is_flag=True, help="dump logs")
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
def ekos(theory_id, datasets, logs, overwrite):
    """Compute EKOs for all FK tables in all datasets."""
    theory.TheoryBuilder(theory_id, datasets, overwrite).ekos(logs)


@theory_.command()
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--pdf", "-p", default=None, help="comparison PDF")
@click.option("--logs", is_flag=True, help="dump comparison")
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
def fks(theory_id, datasets, pdf, logs, overwrite):
    """Compute FK tables in all datasets."""
    theory.TheoryBuilder(theory_id, datasets, overwrite).fks(pdf, logs)

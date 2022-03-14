# -*- coding: utf-8 -*-
import click

from .. import theory
from ._base import command


@command.command("theory_fks")
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--pdf", "-p", default=None, help="comparison PDF")
@click.option("--logs", is_flag=True, help="dump comparison")
def subcommand(theory_id, datasets, pdf, logs):
    """Compute FK tables in all datasets."""
    theory.TheoryBuilder(theory_id, datasets).fks(pdf, logs)

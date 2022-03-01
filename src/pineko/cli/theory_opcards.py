# -*- coding: utf-8 -*-
import click
import pineappl
import rich
import yaml

from .. import evolve
from ._base import command


@command.command("theory_opcards")
@click.argument("datasets", type=click.STRING, nargs=-1)
def subcommand(datasets):
    """Write EKO card for all FK tables in all datasets.
    """
    print(datasets)
    

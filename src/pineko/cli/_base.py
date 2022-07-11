# -*- coding: utf-8 -*-
"""Adds global CLI options."""
import pathlib

import click

from .. import configs

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def command():
    """pineko: Combine PineAPPL grids and EKOs into FK tables."""

# -*- coding: utf-8 -*-
import logging

import click
import eko
import rich
import yaml

from .. import configs, parser, theory_card
from ._base import command


@command.command("theory_ekos")
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--logs", is_flag=True, help="dump logs")
def subcommand(theory_id, datasets, logs):
    """Compute EKOs for all FK tables in all datasets."""
    # setup data
    paths = configs.configs["paths"]
    tcard = theory_card.load(theory_id)
    eko_path = paths["ekos"] / str(theory_id)
    eko_path.mkdir(exist_ok=True)
    # iterate datasets
    for ds in datasets:
        rich.print(f"Analyze {ds}")
        # iterate grids
        grids = parser.load_grids(theory_id, ds)
        for name in grids.keys():
            opcard_path = paths["operator_cards"] / f"{name}.yaml"
            with open(opcard_path, encoding="utf-8") as f:
                ocard = yaml.safe_load(f)
            eko_filename = eko_path / f"{name}.tar"
            # activate logging
            if logs and paths["logs"]["eko"]:
                log_path = paths["logs"]["eko"] / f"{theory_id}-{ds}-{name}.log"
                logStdout = logging.FileHandler(log_path)
                logStdout.setLevel(logging.INFO)
                logStdout.setFormatter(logging.Formatter("%(message)s"))
                logging.getLogger("eko").handlers = []
                logging.getLogger("eko").addHandler(logStdout)
                logging.getLogger("eko").setLevel(logging.INFO)
            # do it!
            ops = eko.run_dglap(theory_card=tcard, operators_card=ocard)
            ops.dump_tar(eko_filename)
            rich.print(f"[green]Success:[/] Wrote EKO to {eko_filename}")
        print()

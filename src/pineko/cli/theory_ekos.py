# -*- coding: utf-8 -*-
import click
import eko
import rich
import yaml

from .. import configs, parser
from ._base import command


@command.command("theory_ekos")
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
def subcommand(theory_id, datasets):
    """Compute EKOs for all FK tables in all datasets."""
    paths = configs.configs.paths
    tcard_path = paths.theory_cards / f"{theory_id}.yaml"
    with open(tcard_path, encoding="utf-8") as f:
        theory_card = yaml.safe_load(f)
    eko_path = paths.ekos / str(theory_id)
    eko_path.mkdir(exist_ok=True)
    for ds in datasets:
        rich.print(f"Analyze {ds}")
        grids = parser.load_grids(theory_id, ds)
        for name, grid in grids.items():
            opcard_path = paths.operator_cards / f"{name}.yaml"
            with open(opcard_path, encoding="utf-8") as f:
                operators_card = yaml.safe_load(f)
            eko_filename = eko_path / f"{name}.tar"
            ops = eko.run_dglap(theory_card=theory_card, operators_card=operators_card)
            ops.dump_tar(eko_filename)
            rich.print(f"[green]Success:[/] Write EKO to {eko_filename}")
        print()

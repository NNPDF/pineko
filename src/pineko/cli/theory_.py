"""'theory' mode of CLI."""
import pathlib

import click

from .. import configs, theory
from ._base import command


@command.group("theory")
@click.option(
    "-c",
    "--configs",
    "cfg",
    default=None,
    type=click.Path(resolve_path=True, path_type=pathlib.Path),
    help="Explicitly specify config file (it has to be a valid TOML file).",
)
def theory_(cfg):
    """Iterate a subcommand on a given theory and list of datasets."""
    path = configs.detect(cfg)
    base_configs = configs.load(path)
    configs.configs = configs.defaults(base_configs)
    if cfg is not None:
        print(f"Configurations loaded from '{path}'")


@theory_.command()
@click.argument("source_theory_id", type=click.INT)
@click.argument("target_theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
def inherit_grids(source_theory_id, target_theory_id, datasets, overwrite):
    """Inherit grids for datasets from one theory to another."""
    theory.TheoryBuilder(source_theory_id, datasets, overwrite=overwrite).inherit_grids(
        target_theory_id
    )


@theory_.command()
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
def opcards(theory_id, datasets, overwrite):
    """Write EKO card for all FK tables in all datasets."""
    theory.TheoryBuilder(theory_id, datasets, overwrite=overwrite).opcards()


@theory_.command()
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--silent", is_flag=True, help="Suppress logs")
@click.option(
    "-cl",
    "--clear-logs",
    is_flag=True,
    help="Erease previos logs (instead of appending)",
)
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
def ekos(theory_id, datasets, silent, clear_logs, overwrite):
    """Compute EKOs for all FK tables in all datasets."""
    theory.TheoryBuilder(
        theory_id, datasets, silent=silent, clear_logs=clear_logs, overwrite=overwrite
    ).ekos()


@theory_.command()
@click.argument("source_theory_id", type=click.INT)
@click.argument("target_theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
def inherit_ekos(source_theory_id, target_theory_id, datasets, overwrite):
    """Inherit ekos from one theory to another."""
    theory.TheoryBuilder(source_theory_id, datasets, overwrite=overwrite).inherit_ekos(
        target_theory_id
    )


@theory_.command()
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--pdf", "-p", default=None, help="PDF set used for comparison")
@click.option("--silent", is_flag=True, help="Suppress logs with comparison")
@click.option(
    "-cl",
    "--clear-logs",
    is_flag=True,
    help="Erease previos logs (instead of appending)",
)
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
def fks(theory_id, datasets, pdf, silent, clear_logs, overwrite):
    """Compute FK tables in all datasets."""
    theory.TheoryBuilder(
        theory_id, datasets, silent=silent, clear_logs=clear_logs, overwrite=overwrite
    ).fks(pdf)


@theory_.command()
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--flavors", "-f", default=5, help="Number of active flavors")
def ren_sv_grids(theory_id, datasets, flavors):
    """Construct new grids with renormalization scale variations included."""
    theory.TheoryBuilder(theory_id, datasets).construct_ren_sv_grids(flavors)

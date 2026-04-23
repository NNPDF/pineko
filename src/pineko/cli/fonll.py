"""CLI entry point to FONLL."""

import rich
import rich_click as click

from .. import fonll, theory, theory_card
from ..fonll import TheoryCardError
from ._base import command, config_option, load_config


@command.group("fonll")
@config_option
def fonll_(cfg):
    """Detect amd load configuration file."""
    load_config(cfg)


@fonll_.command()
@click.argument("theoryID", type=int)
@click.argument("dataset", type=str)
@click.option("--FFNS3", type=int, help="theoryID containing the ffns3 fktable")
@click.option("--FFN03", type=int, help="theoryID containing the ffn03 fktable")
@click.option(
    "--FFNS4zeromass", type=int, help="theoryID containing the ffns4 zeromass fktable"
)
@click.option(
    "--FFNS4massive", type=int, help="theoryID containing the ffns4massive fktable"
)
@click.option("--FFN04", type=int, help="theoryID containing the ffn04 fktable")
@click.option(
    "--FFNS5zeromass", type=int, help="theoryID containing the ffns5 zeromass fktable"
)
@click.option(
    "--FFNS5massive", type=int, help="theoryID containing the ffns5massive fktable"
)
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
def combine(
    theoryid,
    dataset,
    ffns3,
    ffn03,
    ffns4zeromass,
    ffns4massive,
    ffn04,
    ffns5zeromass,
    ffns5massive,
    overwrite,
):
    """Combine the different FKs needed to produce the FONLL prescription."""
    fonll.assembly_combined_fk(
        theoryid,
        dataset,
        ffns3,
        ffn03,
        ffns4zeromass,
        ffns4massive,
        ffn04,
        ffns5zeromass,
        ffns5massive,
        overwrite,
    )


@fonll_.command()
@click.argument("theoryID", type=int)
def tcards(theoryid):
    """Produce the FONLL tcards starting from the original tcard given by the theoryID."""
    tcard = theory_card.load(theoryid)
    tcard_parent_path = theory_card.path(theoryid).parent
    if "FONLL" not in tcard["FNS"]:
        raise TheoryCardError("The theorycard does not correspond to an FONLL scheme.")
    fonll.dump_tcards(tcard, tcard_parent_path, theoryid)


@fonll_.command()
@click.argument("theoryID", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
def ekos(theoryid, datasets, overwrite):
    """Command to generate numerical FONLL ekos.

    1. Create all the operator cards for the different flavor patches.
    2. Run the 3 ekos for the different flavor patches.
    3. Inherit the ekos.
    """
    # Create all the operator cards as they are required for careful testing
    for nf_id in range(7):
        theory.TheoryBuilder(
            f"{theoryid}0{nf_id}", datasets, overwrite=overwrite
        ).opcards()

    # Most of the time only these 3 patches are necessary
    for nf_id in ["00", "04", "05"]:
        # run the ekos
        theory.TheoryBuilder(
            f"{theoryid}{nf_id}",
            datasets,
            silent=False,
            clear_logs=True,
            overwrite=overwrite,
        ).ekos()

    # Now _attempt_ to inherit the ekos
    # _if_ a discrepancy is found between the eko and the grid, recompute

    inheritance_map = {"00": ["01"], "04": ["02", "03"], "05": ["06"]}
    for i, (source, targets) in enumerate(inheritance_map.items()):
        source_tid = f"{theoryid}{source}"
        rich.print(f"[green] Inherit nf={3+i} ekos from theory {source_tid}")
        source_theory = theory.TheoryBuilder(source_tid, datasets, overwrite=overwrite)
        for target in targets:
            target_tid = f"{theoryid}{target}"
            try:
                source_theory.inherit_ekos(target_tid, careful=True)
            except AssertionError as e:
                rich.print(
                    f"[red] Could not inherit from theory {source_tid} to {target_tid}, computing the EKO"
                )
                theory.TheoryBuilder(
                    target_tid,
                    datasets,
                    silent=False,
                    clear_logs=True,
                    overwrite=overwrite,
                ).ekos()


@fonll_.command()
@click.argument("theoryID", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option(
    "--pdfs",
    "-p",
    default=None,
    type=click.STRING,
    help="List of PDF sets to be used for comparison; single string where sets are separated by commas",
)
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
def fks(theoryid, datasets, pdfs, overwrite):
    """Command to generate numerical FONLL FK tables.

    1. Produce the 7 FK tables needed for numerical FONLL.
    2. Combine the FKtables into a single one.
    """
    # create the 7 FK tables
    pdfs = pdfs.split(",") if pdfs is not None else pdfs
    for th_suffix in range(0, 7):
        theory.TheoryBuilder(  # [too-many-function-args]
            f"{theoryid}0{th_suffix}",
            datasets,
            silent=False,
            clear_logs=True,
            overwrite=overwrite,
        ).fks(pdfs)

    # combine
    for dataset in datasets:
        fonll.assembly_combined_fk(
            theoryid,
            dataset,
            ffns3=f"{theoryid}00",
            ffn03=f"{theoryid}01",
            ffns4zeromass=f"{theoryid}02",
            ffns4massive=f"{theoryid}03",
            ffn04=f"{theoryid}04",
            ffns5zeromass=f"{theoryid}05",
            ffns5massive=f"{theoryid}06",
            overwrite=overwrite,
        )

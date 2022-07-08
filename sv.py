# -*- coding: utf-8 -*-
import pathlib

import click
import lhapdf
import numpy as np
import pandas as pd
import pineappl

# global settings
here = pathlib.Path(__file__).parent
fk_path = here / "data" / "fktables"
fk_name = "test"
# fk_name = "HERA_CC_318GEV_EM_SIGMARED"
# fk_name = "HERA_NC_225GEV_EP_SIGMARED"
is_dis = True


@click.command()
@click.argument("order", type=int)
@click.argument("value", type=float)
@click.option("--abs", is_flag=True, help="keep absolute values")
def run(order, value, abs):
    # derive order specific settings
    if order == 2:
        pdf_name = "NNPDF40_nnlo_as_01180"
        central = 200
        theories = {"A": 10200, "B": 20200, "C": 30200}
    else:
        pdf_name = "gonly"
        central = 4001
        if np.isclose(value, np.sqrt(2), atol=0.05):
            theories = {"A": 1140, "B": 2140, "C": 3140}
        else:
            theories = {"B": 2201, "C": 3201}

    # derive common settings
    pdf = lhapdf.mkPDF(pdf_name, 0)
    pdgid = int(pdf.set().get_entry("Particle"))

    # collect central
    df = pd.DataFrame()
    fk = pineappl.fk_table.FkTable.read(
        fk_path / str(central) / f"{fk_name}.pineappl.lz4"
    )
    for bd in range(fk.bin_dimensions()):
        df[f"b{bd} l"] = fk.bin_left(bd)
        if not is_dis:
            df[f"b{bd} r"] = fk.bin_right(bd)
    df["central"] = fk.convolute_with_one(pdgid, pdf.xfxQ2)

    # collect SVs
    for tn, ti in theories.items():
        fk_sv = pineappl.fk_table.FkTable.read(
            fk_path / str(ti) / f"{fk_name}.pineappl.lz4"
        )
        df[tn] = fk_sv.convolute_with_one(pdgid, pdf.xfxQ2)
        df[f"{tn}2central [%]"] = (df[tn] / df["central"] - 1.0) * 100.0
    # df["ΔA2ΔC [%]"] = (
    #     (df["A"] - df["central"]) / (df["C"] - df["central"]) - 1.0
    # ) * 100.0
    df["ΔB2ΔC [%]"] = (
        (df["B"] - df["central"]) / (df["C"] - df["central"]) - 1.0
    ) * 100.0

    # remove predictions
    if not abs:
        for tn in theories.keys():
            del df[tn]

    print(df.to_string())


if __name__ == "__main__":
    run()

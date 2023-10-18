import lhapdf
import pineappl
from glob import glob
from datetime import datetime as dt
import numpy as np
import os
import argparse


def get_gpaths(folder):
    """
    Get a list of paths to PineAPPL grids in the specified folder.

    Args:
        folder (str): The folder path where PineAPPL grids are located.

    Returns:
        pdf_name (str): The name of the PDF dataset.
        gpaths (list): List of paths to PineAPPL grid files.
    """
    paths = glob(folder + "/*F1*")  # Find grids with "_F1" in the filename
    gpaths = []
    for p in paths:
        gpaths.append(glob(p + "/*.pineappl.lz4")[0])
    print(f"Found {len(gpaths)} pineapple grids.")
    return pdf_name, gpaths


def get_prediction(gpath, pdf_name):
    """
    Get predictions by convoluting a PineAPPL grid with a LHAPDF PDF.

    Args:
        gpath (str): Path to the PineAPPL grid file.
        pdf_name (str): The name of the LHAPDF dataset.

    Returns:
        prediction (numpy.ndarray): Computed predictions.
    """
    # Load the PineAPPL grid
    grid = pineappl.grid.Grid.read(gpath)

    # Load the LHAPDF
    pdf = lhapdf.mkPDF(pdf_name)

    # Perform the convolution
    prediction = grid.convolute_with_one(
        2212,  # Proton target
        pdf.xfxQ2,  # The PDF callable pdf.xfxQ2(pid, x, Q2) -> xfx
        pdf.alphasQ2,  # The alpha_s callable pdf.alpha_s(Q2) -> alpha_s
    )

    # Compute the k-factor (1 / F1)
    prediction = 1 / prediction

    return prediction


def save_data(
    data,
    dataset_name="<Name_of_dataset>",
    author_name="<Your_name>",
    theory_name="<Theory_name>",
    output_name="results",
):
    """
    Save computed data to a file with metadata.

    Args:
        data (numpy.ndarray): Computed data.
        dataset_name (str): Name of the dataset.
        author_name (str): Name of the author.
        theory_name (str): Name of the theory.
        output_name (str): Output folder name.
    """
    strf_data = ""
    for i in range(data.shape[0]):
        strf_data += f"{data[i]}  0.0\n"

    date = dt.now().date()
    string = (
        f"""
********************************************************************************
SetName: {dataset_name}
Author: {author_name}
Date: {date}
CodesUsed: https://github.com/NNPDF/yadism
TheoryInput: {theory_name}
PDFset: NNPDF40_nnlo_pch_as_01180
Warnings: F1 normalization for {dataset_name}
********************************************************************************
"""
        + strf_data
    )

    os.makedirs(output_name, exist_ok=True)
    with open(output_name + f"/CF_QCD_{dataset_name}.dat", "w") as file:
        file.write(string)


# Create an argument parser
parser = argparse.ArgumentParser()
parser.add_argument("pdf", help="The name of the PDF dataset of LHAPDF")
parser.add_argument("folder", help="The folder name of the F1 pineapple grids")
parser.add_argument("--author", default="A.J. Hasenack")
parser.add_argument("--theory", default="theory_800")
parser.add_argument("--output", default="results")
args = parser.parse_args()

# Extract command line arguments
pdf_name = args.pdf
folder_name = args.folder
author = args.author
theory = args.theory
output = args.output

# Get PineAPPL grid paths and PDF name
pdf_name, gpaths = get_gpaths(folder_name)

# Process each PineAPPL grid
for gpath in gpaths:
    dataset_name = os.path.splitext(
        os.path.splitext(os.path.basename(os.path.normpath(gpath)))[0]
    )[0]

    # Get predictions and save data
    data = get_prediction(gpath, pdf_name)
    save_data(data, dataset_name, author, theory, output)

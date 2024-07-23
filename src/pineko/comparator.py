"""Tools to compare grids and FK tables."""

import numpy as np
import pandas as pd
import pineappl


def compare(pine, fktable, max_as, max_al, pdf1, xir, xif, pdf2=None):
    """Build comparison table.

    Parameters
    ----------
    pine : pineappl.grid.Grid
        uncovoluted grid
    fktable : pineappl.fktable.FkTable
        convolved grid
    max_as : int
        maximum power of strong coupling
    max_al : int
        maximum power of electro-weak coupling
    pdf1 : str
        PDF set name
    xir : float
        renormalization scale variation
    xif : float
        factorization scale variation
    pdf2: str or None
        PDF set for the second convolution, if different from the first

    Returns
    -------
    df : pd.DataFrame
        comparison table
    """
    import lhapdf  # pylint: disable=import-error,import-outside-toplevel

    pdfset1 = lhapdf.mkPDF(pdf1, 0)
    pdgid1 = int(pdfset1.set().get_entry("Particle"))

    if pdf2 is not None:
        pdfset2 = lhapdf.mkPDF(pdf1, 0)
        pdgid2 = int(pdfset2.set().get_entry("Particle"))
    else:
        pdfset2 = pdfset1
        pdgid2 = pdgid1

    try:
        parton1 = pine.key_values()["convolution_particle_1"]
        parton2 = pine.key_values()["convolution_particle_2"]
    except KeyError:
        parton1 = pine.key_values()["initial_state_1"]
        parton2 = pine.key_values()["initial_state_2"]
    hadronic = parton1 == parton2

    order_mask = pineappl.grid.Order.create_mask(pine.orders(), max_as, max_al, True)
    if hadronic:
        before = np.array(
            pine.convolve_with_two(
                pdgid1,
                pdfset1.xfxQ2,
                pdfset1.alphasQ2,
                pdgid2,
                pdfset2.xfxQ2,
                pdfset2.alphasQ2,
                order_mask=order_mask,
                xi=((xir, xif),),
            )
        )
        after = np.array(
            fktable.convolve_with_one(pdgid1, pdfset1.xfxQ2, pdgid2, pdfset2.xfxQ2)
        )
    else:
        before = np.array(
            pine.convolve_with_one(
                pdgid1,
                pdfset1.xfxQ2,
                pdfset1.alphasQ2,
                order_mask=order_mask,
                xi=((xir, xif),),
            )
        )
        after = np.array(fktable.convolve_with_one(pdgid1, pdfset1.xfxQ2))

    df = pd.DataFrame()
    # add bin info
    for d in range(pine.bin_dimensions()):
        try:
            label = pine.key_values()[f"x{d+1}_label"]
        except KeyError:
            label = f"O{d+1}"
        df[f"{label} left"] = pine.bin_left(d)
        df[f"{label} right"] = pine.bin_right(d)
    # add data
    df["PineAPPL"] = before
    df["FkTable"] = after
    df["permille_error"] = (after / before - 1.0) * 1000.0
    return df

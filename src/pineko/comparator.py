"""Tools to compare grids and FK tables."""

import numpy as np
import pandas as pd
import pineappl


def compare(pine, fktable, max_as, max_al, pdf, xir, xif):
    """Build comparison table.

    Parameters
    ----------
    pine : pineappl.grid.Grid
        uncovoluted grid
    fktable : pineappl.fktable.FkTable
        convoluted grid
    max_as : int
        maximum power of strong coupling
    max_al : int
        maximum power of electro-weak coupling
    pdf : str
        PDF set name
    xir : float
        renormalization scale variation
    xif : float
        factorization scale variation

    Returns
    -------
    df : pd.DataFrame
        comparison table
    """
    import lhapdf  # pylint: disable=import-error

    pdfset = lhapdf.mkPDF(pdf, 0)
    pdgid = int(pdfset.set().get_entry("Particle"))
    order_mask = pineappl.grid.Order.create_mask(pine.orders(), max_as, max_al, True)
    before = np.array(
        pine.convolute_with_one(
            pdgid,
            pdfset.xfxQ2,
            pdfset.alphasQ2,
            order_mask=order_mask,
            xi=((xir, xif),),
        )
    )
    after = np.array(fktable.convolute_with_one(pdgid, pdfset.xfxQ2))
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

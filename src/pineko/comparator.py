import numpy as np
import pandas as pd

import pineappl


def compare(pine, fktable, pdf):
    """
    Build comparison table.

    Parameters
    ----------
        pine : pineappl.grid.Grid
            uncovoluted grid
        fktable : pineappl.fktable.FkTable
            convoluted grid
        pdf : str
            PDF set name

    Returns
    -------
        df : pd.DataFrame
            comparison table
    """
    import lhapdf  # pylint: disable=import-outside-toplevel

    pdfset = lhapdf.mkPDF(pdf, 0)
    pdgid = int(pdfset.set().get_entry("Particle"))
    order_mask = pineappl.grid.Order.create_mask(pine.orders(), 2, 0)
    before = np.array(
        pine.convolute_with_one(
            pdgid, pdfset.xfxQ2, pdfset.alphasQ2, order_mask=order_mask
        )
    )
    after = np.array(fktable.convolute_with_one(pdgid, pdfset.xfxQ2))
    df = pd.DataFrame()
    # add bin info
    for d in range(pine.bin_dimensions()):
        df[f"O{d} left"] = pine.bin_left(d)
        df[f"O{d} right"] = pine.bin_right(d)
    # add data
    df["PineAPPL"] = before
    df["FkTable"] = after
    df["percent_error"] = (after / before - 1.0) * 100.0
    return df

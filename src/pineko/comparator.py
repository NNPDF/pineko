import numpy as np
import pandas as pd


def compare(pineappl, fktable, pdf):
    """
    Build comparison table.

    Parameters
    ----------
        pineappl_path : str
            uncovoluted grid
        fktable_path : str
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
    before = np.array(pineappl.convolute_with_one(pdgid, pdfset.xfxQ2, pdfset.alphasQ2))
    after = np.array(fktable.convolute_with_one(pdgid, pdfset.xfxQ2))
    df = pd.DataFrame()
    # add bin info
    for d in range(pineappl.bin_dimensions()):
        df[f"O{d} left"] = pineappl.bin_left(d)
        df[f"O{d} right"] = pineappl.bin_right(d)
    # add data
    df["PineAPPL"] = before
    df["FkTable"] = after
    df["percent_error"] = (after / before - 1.0) * 100.0
    return df

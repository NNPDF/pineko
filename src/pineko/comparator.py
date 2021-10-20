import numpy as np
import pandas as pd
import eko.basis_rotation as br


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
    before = np.array(
        pineappl.convolute(pdfset.xfxQ2, lambda pdg_id, x, q2: 1.0, pdfset.alphasQ2)
    )
    after = np.array(
        fktable.convolute(
            pdfset.xfxQ2,
            lambda pdg_id, x, q2: 1.0,
        )
    )
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

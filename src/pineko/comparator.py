import numpy as np
import pandas as pd

def order_finder(pine):
    """
    Returns masks for LO+QCD and EW.
    
    Parameters
    ----------
        pine : pineappl.grid.Grid
            PineAPPL grid

    Returns
    -------
        mask_qcd : list(bool)
            LO + QCD
        mask_ew : list(bool)
            EW
    """
    qcd = np.array([1,0,0,0])
    ew = np.array([0,1,0,0])
    orders = [np.array(orde.as_tuple()) for orde in pine.orders()]
    LO = orders[0]
    mask_qcd = [True] + [False]*(len(orders)-1)
    mask_ew = [False] + [False]*(len(orders)-1)
    for i, order in enumerate(orders):
        if np.allclose(order, LO+qcd):
            mask_qcd[i] = True
        if np.allclose(order, LO+ew):
            mask_ew[i] = True
    return mask_qcd, mask_ew

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
    order_mask_qcd, _ = order_finder(pineappl)
    before = np.array(pineappl.convolute_with_one(pdgid, pdfset.xfxQ2, pdfset.alphasQ2, order_mask=order_mask_qcd))
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

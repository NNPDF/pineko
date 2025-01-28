"""Tools to compare grids and FK tables."""

import numpy as np
import pandas as pd
import pineappl


class GridtoFKError(Exception):
    """Raised when the difference between the Grid and FK table is above some threshold."""


def compare(pine, fktable, max_as, max_al, pdfs, scales, threshold=5.0):
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
    pdfs : list(str)
        list of the PDF set names
    scales: tuple
        contains the values the renormalization, factorization, and fragmentation scale
        variations
    threshold: float
        check if the difference between the Grid and FK table is above the
        threshold then raise an error

    Returns
    -------
    df : pd.DataFrame
        comparison table
    """
    import lhapdf  # pylint: disable=import-error,import-outside-toplevel

    pdfsets = [lhapdf.mkPDF(pdf, 0) for pdf in pdfs]

    # Check compatibilty between the FK table and the grid
    assert len(fktable.convolutions) == len(
        pine.convolutions
    ), "FK table and Grid have different (number of) convolutions"

    for gconv, fconv in zip(pine.convolutions, fktable.convolutions):
        if gconv.conv_type.polarized != fconv.conv_type.polarized:
            raise ValueError(
                "The Grid and FK table do not have the same type of Polarization:"
                f"grid={gconv.conv_type.polarized} vs. fk={fconv.conv_type.polarized}"
            )
        if gconv.conv_type.time_like != fconv.conv_type.time_like:
            raise ValueError(
                "The Grid and FK table do not have the same type of Interval:"
                f"grid={gconv.conv_type.time_like} vs. fk={fconv.conv_type.time_like}"
            )

    # TODO: Add checks that verify the compatibility with the PDFs
    order_mask = pineappl.boc.Order.create_mask(
        orders=pine.orders(), max_as=max_as, max_al=max_al, logs=True
    )
    # Perform the convolutions of the Grids and FK tables (This is now much simpler!)
    pine_predictions = pine.convolve(
        pdg_convs=pine.convolutions,
        xfxs=[pdf.xfxQ2 for pdf in pdfsets],
        alphas=pdfsets[0].alphasQ2,  # TODO: Choose which PDF should be used
        order_mask=order_mask,
        xi=[scales],  # TODO: Exposes as a list
    )
    fktable_predictions = fktable.convolve(
        pdg_convs=fktable.convolutions,
        xfxs=[pdf.xfxQ2 for pdf in pdfsets],
    )
    before = np.array(pine_predictions)
    after = np.array(fktable_predictions)

    df = pd.DataFrame()
    # add bin info
    for d in range(pine.bin_dimensions()):
        df[f"O{d+1} left"] = pine.bin_left(d)
        df[f"O{d+1} right"] = pine.bin_right(d)
    # add data
    df["PineAPPL"] = before
    df["FkTable"] = after
    df["permille_error"] = (after / before - 1.0) * 1000.0

    if (df["permille_error"].abs() >= threshold).any():
        raise GridtoFKError(
            f"The difference between the Grid and FK is above {threshold} permille."
        )

    return df

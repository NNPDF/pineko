import io
import subprocess

import numpy as np
import pandas as pd


def build_data_frame(full_output):
    """
    Parse a Rust table into a `pd.DataFrame`.

    Parameters
    ----------
        full_output : str
            console output

    Returns
    -------
        df : pd.DataFrame
            data frame
    """
    # split by lines
    output = full_output.splitlines()
    stream = io.StringIO()
    # determine columns
    columns = [[e.strip(), e.strip() + "_2"] for e in output[2].split()[1:]]
    columns = ["bin"] + [f for e in columns for f in e] + ["pine", "fk", "reldiff"]
    # get rid of all the white space
    for line in output[4:-2]:
        stream.write(" ".join([e.strip() for e in line.split()]) + "\n")
    # setup dataframe
    stream.seek(0)
    return pd.read_table(stream, names=columns, sep=" ")


def compare(pineappl_path, fktable_path, pdf):
    """
    Build comparison table via `pineappl diff`.

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
    # get the output
    comparison = subprocess.run(
        [
            "pineappl",
            "diff",
            "--ignore_orders",
            str(pineappl_path),
            str(fktable_path),
            pdf,
        ],
        capture_output=True,
    )
    # parse to data frame
    df = build_data_frame(comparison.stdout.decode())
    df.set_index("bin", inplace=True)
    # remove bins' upper edges when bins are trivial
    obs_labels = np.unique(
        [lab for lab in filter(lambda lab: "_" in lab and "my" not in lab, df.columns)]
    )
    df.drop(obs_labels, axis=1, inplace=True)
    # print("\n".join(output))
    return df

def compare2(pineappl, fktable, pdf):
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
    import lhapdf
    pdfset = lhapdf.mkPDF(pdf, 0)
    before = pineappl.convolute(
        pdfset.xfxQ2,
        lambda pdg_id, x, q2: 1.0,
        pdfset.alphasQ2
    )
    after = fktable.convolute(
        lambda pdg_id, x, q2: pdfset.xfxQ2(pdg_id, x, q2),
        lambda pdg_id, x, q2: 1.0,
        lambda q2: pdfset.alphasQ2(q2)
    )
    df = pd.DataFrame()
    # add bin info
    for d in range(pineappl.bin_dimensions()):
        df[f"O{d} left"] = pineappl.bin_left(d)
        df[f"O{d} right"] = pineappl.bin_right(d)
    # add data
    df["PineAPPL"] = before
    df["FkTable"] = after
    return df

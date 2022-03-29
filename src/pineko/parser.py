"""
    Loader for pineappl-based FKTables

    The FKTables for pineappl have ``pineappl.lz4`` as extension and can be utilized
    directly with the ``pineappl`` cli as well as read with ``pineappl.fk_table``

    Examples
    --------
    >>> from pathlib import Path
    >>> from pineko.parser import get_yaml_information, pineappl_to_fktable
    >>> dataset = "ATLAS_TTB_DIFF_8TEV_LJ_TRAPNORM"
    >>> yaml_folder = Path("/usr/local/share/NNPDF/data/yamldb")
    >>> pine_folder = Path("/usr/local/share/NNPDF/data/theory_200/pineappls/")
    >>> yaml_file = yaml_folder / f"{dataset}.yaml"
    >>> yaml_info, paths = get_yaml_information(yaml_file, pine_folder)
    >>> fk = pineappl_to_fktable(yaml_info, paths[0])
    >>> fk.dataframe
15         16        17        18   ...       167       180       181       195
data x1 x2                                           ...                                        
0    0  0   0.000000   0.000000  0.000000  0.000000  ...  0.000000  0.000000  0.000000  0.000000
        1   0.000000   0.000000  0.000000  0.000000  ...  0.000000  0.000000  0.000000  0.000000
        2   0.000000   0.000000  0.000000  0.000000  ...  0.000000  0.000000  0.000000  0.000000
        3   0.000000   0.000000  0.000000  0.000000  ...  0.000000  0.000000  0.000000  0.000000
        4   0.000000   0.000000  0.000000  0.000000  ...  0.000000  0.000000  0.000000  0.000000
...              ...        ...       ...       ...  ...       ...       ...       ...       ...
4    99 95  0.000000  -0.724031 -0.000224  0.000140  ... -0.002200  0.000000 -0.013380  0.000000
        96  0.000000  -0.722401 -0.000193 -0.000007  ... -0.002141  0.000000 -0.014283  0.000000
        97  0.000000  -0.513297 -0.000059  0.000128  ... -0.001426  0.000000 -0.010557  0.000000
        98  0.000000  -0.841811  0.000018  0.000349  ... -0.002255  0.000000 -0.016986  0.000000
        99 -0.004565  74.340392  0.001172 -0.002813  ... -0.015495 -0.000411 -0.000548 -0.000183
"""
from collections import namedtuple
import yaml
import numpy as np
import pandas as pd

from eko.basis_rotation import evol_basis_pids
from pineappl.fk_table import FkTable

EXT = "pineappl.lz4"

FkData = namedtuple("FkData", ["dataframe", "q0", "xgrid"])


class YamlFileNotFound(FileNotFoundError):
    """ymldb file for dataset not found."""


class GridFileNotFound(FileNotFoundError):
    """PineAPPL file for FK table not found."""


def _load_yaml(yaml_file):
    """Load a dataset.yaml file.

    Parameters
    ----------
    yaml_file : Path
        path of the yaml file for the given dataset

    Returns
    -------
    dict :
        noramlized parsed file content
    """
    if not yaml_file.exists():
        raise YamlFileNotFound(yaml_file)
    ret = yaml.safe_load(yaml_file.read_text())
    # Make sure the operations are upper-cased for compound-compatibility
    ret["operation"] = "NULL" if ret["operation"] is None else ret["operation"].upper()
    return ret


def _apfelcomb_compatibility_flags(gridpaths, metadata):
    """
    Prepare the apfelcomb-pineappl compatibility fixes

    Returns
    -------
        apfelcomb_norm: np.array
            Per-point normalization factor to be applied to the grid
            to be compatible with the data
        apfelcomb_repetition_flag: bool
            Whether the fktable is a single point which gets repeated up to a certain size
            (for instance to normalize a distribution)
        shift: list(int)
            Shift in the data index for each grid that forms the fktable
    """
    operands = metadata["operands"]
    apfelcomb_norm = None
    if norms := metadata.get("apfelcomb_norm"):
        # There's no easy way for an fktable to know its role in given operation:
        for factors, grids in zip(norms, operands):
            # Now check, in case of an operation, what is our index in this operation
            if len(grids) == len(gridpaths) and all(
                f.name == f"{o}.{EXT}" for f, o in zip(gridpaths, grids)
            ):
                apfelcomb_norm = np.array(factors)

    # Check for the repetition flag, meaning we only want the first datapoint for this fktable
    apfelcomb_repetition_flag = False
    if metadata.get("repetition_flag"):
        valid_targets = []
        for operand, flagged in zip(operands, metadata["repetition_flag"]):
            if flagged:
                valid_targets.append(f"{operand[0]}.{EXT}")
        # Now check whether the current fktable is part of the valid targets
        apfelcomb_repetition_flag = gridpaths[0].name in valid_targets
        if apfelcomb_repetition_flag and len(gridpaths) > 1:
            raise ValueError(f"Repetition set for a group of fktables at once: {gridpaths}")

    # afaik there's only dataset with shifts, but it needs to be considered
    shifts = None
    if metadata.get("shifts"):
        if len(operands) > 1:
            raise ValueError("Wrong shifts for {metadata['target_dataset']}")
        shifts = [0 if shift is None else shift for shift in metadata["shifts"][0]]
    return apfelcomb_norm, apfelcomb_repetition_flag, shifts


def get_yaml_information(yaml_file, grids_folder, check_grid_existence=True):
    """Given a yaml_file, returns the corresponding dictionary and grids.

    The dictionary contains all information and we return an extra field
    with all the grids to be loaded for the given dataset.

    Parameters
    ----------
    yaml_file : pathlib.Path
        path of the yaml file for the given dataset
    grids_folder : pathlib.Path
        path of the grids folder
    check_grid_existence: bool
        if True (default) checks whether the grid exists

    Returns
    -------
    yaml_content: dict
        Metadata prepared for the FKTables
    paths: list(list(path))
        List (of lists) with all the grids that will need to be loaded
    """
    yaml_content = _load_yaml(yaml_file)

    # Turn the operands and the members into paths (and check all of them exist)
    ret = []
    for operand in yaml_content["operands"]:
        tmp = []
        for member in operand:
            p = grids_folder / f"{member}.{EXT}"
            if not p.exists() and check_grid_existence:
                raise GridFileNotFound(f"Failed to find {p}")
            tmp.append(p)
        ret.append(tmp)

    return yaml_content, ret


def _pinelumi_to_columns(pine_luminosity, hadronic, flav_size=14):
    """Makes the pineappl luminosity into the column indices of a dataframe
    These corresponds to the indices of a flat (14x14) matrix for hadronic observables
    and the non-zero indices of the 14-flavours for DIS

    Parameters
    ----------
        pine_luminosity: list(tuple)
            list with a pair of flavours per channel
        hadronic: bool
            flag for hadronic / DIS observables

    Returns
    -------
        list(int): list of indices
    """
    co = []
    if hadronic:
        for i, j in pine_luminosity:
            idx = evol_basis_pids.index(i)
            jdx = evol_basis_pids.index(j)
            co.append(flav_size * idx + jdx)
    else:
        # The proton might come from both sides
        try:
            co = [evol_basis_pids.index(i) for _, i in pine_luminosity]
        except ValueError:
            co = [evol_basis_pids.index(i) for i, _ in pine_luminosity]
    return co


def pineappl_to_fktable(metadata, pinepaths):
    """Receives a list of paths to pineappl grids and returns the information
    in the form of a pandas dataframe that can be easily parsed by external progams

    Returns a FkData object that contains some general metadata (Q0 of the grid, xgrid)
    as well as the fktable made into a dataframe.

    The dataframe contains a column per active luminosity channel, corresponding to the indices
    of a 14x(14) matrix in the evolution basis.
    The indices of the dataframe are [data, x1, (x2)].

    Note: the metadata correspond to a commondata file and so it can contain many partial
    observables as operators that, at the end, give raise to a single observable
    (for instance a differential cross section normalized to the total)
    The paths correspond to only one of these observables.

    Parameters
    ----------
        metadata: dict
            metadata information for the dataset (usually the output of get_yaml_information)
        pinepaths: list(pathlib.Path)
            list of paths to pineappl grids
    """
    # Read each of the pineappl fktables
    pines = [FkTable.read(i) for i in pinepaths]

    # Extract some theory metadata from the first grid
    pine_rep = pines[0]
    hadronic = pine_rep.key_values()["initial_state_1"] == pine_rep.key_values()["initial_state_2"]
    # Sanity check (in case at some point we start fitting things that are not protons)
    if hadronic and pine_rep.key_values()["initial_state_1"] != "2212":
        raise ValueError(
            "pineappl_reader is not prepared to read a hadronic fktable with no protons!"
        )
    Q0 = np.sqrt(pine_rep.muf2())
    xgrid = pine_rep.x_grid()
    # fktables in pineapplgrid are for o = fk * f while previous fktables were o = fk * xf
    # prepare the grid all tables will be divided by
    if hadronic:
        xdivision = (xgrid[:, None] * xgrid[None, :]).flatten()
    else:
        xdivision = xgrid

    apfelcomb_norm, apfelcomb_repetition_flag, shifts = _apfelcomb_compatibility_flags(
        pinepaths, metadata
    )

    # Read each separated grid and luminosity
    fktables = []
    ndata = 0
    for i, p in enumerate(pines):
        luminosity_columns = _pinelumi_to_columns(p.lumi(), hadronic)

        # Remove the bin normalization
        raw_fktable = (p.table().T / p.bin_normalizations()).T
        n = raw_fktable.shape[0]
        lf = len(luminosity_columns)

        # Apply the apfelcomb fixes
        if apfelcomb_norm is not None:
            raw_fktable = (raw_fktable.T * apfelcomb_norm[ndata : ndata + n]).T
        if apfelcomb_repetition_flag:
            raw_fktable = raw_fktable[0:1]
            n = 1
        if shifts is not None:
            ndata += shifts[i]
        ###

        partial_fktable = raw_fktable.reshape(n, lf, -1) / xdivision

        # Now concatenate (data, x1, x2) and move the flavours to the columns
        df_fktable = partial_fktable.swapaxes(0, 1).reshape(lf, -1).T

        # Create the multi-index for the dataframe
        ni = np.arange(ndata, n + ndata)
        xi = np.arange(len(xgrid))
        if hadronic:
            idx = pd.MultiIndex.from_product([ni, xi, xi], names=["data", "x1", "x2"])
        else:
            idx = pd.MultiIndex.from_product([ni, xi], names=["data", "x"])

        df_fktable *= metadata.get("conversion_factor", 1.0)

        fktables.append(pd.DataFrame(df_fktable, columns=luminosity_columns, index=idx))
        ndata += n

    # Finallly concatenate all fktables, sort by flavours and fill any holes
    df = pd.concat(fktables, sort=True, copy=False).fillna(0.0)

    return FkData(df, Q0, xgrid)

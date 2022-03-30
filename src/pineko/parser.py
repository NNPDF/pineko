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
from dataclasses import dataclass
import yaml
import numpy as np

from eko.basis_rotation import evol_basis_pids
from pineappl.fk_table import FkTable

EXT = "pineappl.lz4"


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

    These fixes can be of only three types:

    - normalization:
        normalization per subgrid

        normalization:
            grid_name: factor

    - repetition_flag:
        when a grid was actually the same point repeated X times
        NNPDF cfactors and cuts are waiting for this repetition and so we need to keep track of it

        repetition_flag:
            grid_name

    - shifts:
        only for ATLASZPT8TEVMDIST
        at some point a grid was eliminated in the middle and so the indices for the points are shifted

        shifts:
            grid_name: shift_int

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
    if metadata.get("apfelcomb") is None:
        return None

    # Can't pathlib understand double suffixes?
    operands = [i.name.replace(f".{EXT}", "") for i in gridpaths]
    ret = {}

    # Check whether we have a normalization active and whether it affects any of the grids
    if metadata["apfelcomb"].get("normalization") is not None:
        norm_info = metadata["apfelcomb"]["normalization"]
        # Now fill the operands that need normalization
        ret["normalization"] = [norm_info.get(op, 1.0) for op in operands]

    # Check whether the repetition flag is active
    if metadata["apfelcomb"].get("repetition_flag") is not None:
        if len(operands) == 1:
            ret["repetition_flag"] = operands[0] in metadata["apfelcomb"]["repetition_flag"]
        else:
            # Just for the sake of it, let's check whether we did something stupid
            if any(op in metadata["apfelcomb"]["repetition_flag"] for op in operands):
                raise ValueError(f"The yaml info for {metadata['target_dataset']} is broken")

    # Check whether the dataset has shifts
    # Note: this only happens for ATLASZPT8TEVMDIST, if that gets fixed we might as well remove it
    if metadata["apfelcomb"].get("shifts") is not None:
        shift_info = metadata["apfelcomb"]["shifts"]
        ret["shifts"] = [shift_info.get(op, 0) for op in operands]

    return ret


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


def _pinelumi_to_columns(pine_luminosity, hadronic):
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
        list(int): list of labels for the columns
    """
    flav_size = len(evol_basis_pids)
    columns = []
    if hadronic:
        for i, j in pine_luminosity:
            idx = evol_basis_pids.index(i)
            jdx = evol_basis_pids.index(j)
            columns.append(flav_size * idx + jdx)
    else:
        # The proton might come from both sides
        try:
            columns = [evol_basis_pids.index(i) for _, i in pine_luminosity]
        except ValueError:
            columns = [evol_basis_pids.index(i) for i, _ in pine_luminosity]
    return columns


@dataclass
class FkData:
    """The FkData contains information to regenerate a dataframe

    It contains:

        fktables: list(np.ndarray)
            list of rank-4 tensors with (data, channels, x, x)
        luminosities: list(list(int))
            luminosity channels active for each of the previous fktables
        data_indices: list(np.ndarray)
            list of data indices for each of the fktables
        q0: float
            scale for this fktable
        hadronic: bool
            whether the observable is hadronic
        protected: bool
            whether the observable accepts cuts
    """

    fktables: list
    luminosities: list
    data_indices: list  # needed because of the shifts!
    q0: float
    xgrid: np.ndarray
    hadronic: bool = False
    protected: bool = False

    def __iter__(self):
        return zip(self.fktables, self.luminosities, self.data_indices)


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

    protected = False
    apfelcomb = _apfelcomb_compatibility_flags(pinepaths, metadata)

    # Read each separated grid and luminosity
    fktables = []
    luminosity_channels = []
    data_indices = []
    ndata = 0

    # fktables in pineapplgrid are for o = fk * f while previous fktables were o = fk * xf
    # prepare the grid all tables will be divided by
    if hadronic:
        xdivision = np.prod(np.meshgrid(xgrid, xgrid), axis=0)
    else:
        xdivision = xgrid[:, np.newaxis]

    for i, p in enumerate(pines):
        luminosity_columns = _pinelumi_to_columns(p.lumi(), hadronic)

        # Remove the bin normalization
        raw_fktable = (p.table().T / p.bin_normalizations()).T
        n = raw_fktable.shape[0]

        # Apply the apfelcomb fixes if they are needed
        if apfelcomb is not None:
            if apfelcomb.get("normalization") is not None:
                raw_fktable = raw_fktable * apfelcomb["normalization"][i]
            if apfelcomb.get("repetition_flag", False):
                raw_fktable = raw_fktable[0:1]
                n = 1
                protected = True
            if apfelcomb.get("shifts") is not None:
                ndata += apfelcomb["shifts"][i]
        ###

        # Check conversion factors and remove the x* from the fktable
        raw_fktable *= metadata.get("conversion_factor", 1.0) / xdivision

        luminosity_channels.append(luminosity_columns)
        fktables.append(raw_fktable)
        data_indices.append(np.arange(ndata, ndata + n))

        ndata += n

    return FkData(fktables, luminosity_channels, data_indices, Q0, xgrid, hadronic, protected)

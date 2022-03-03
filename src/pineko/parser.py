# -*- coding: utf-8 -*-
# ATTENTION: this is a partial copy from
# https://github.com/NNPDF/nnpdf/blob/ec73c9c5d3765c8b600e3015d3f5d6238dd89400/validphys2/src/validphys/fkparser.py

import yaml

from . import configs

ext = "pineappl.lz4"


class PineAPPLEquivalentNotKnown(Exception):
    pass


class YamlFileNotFound(FileNotFoundError):
    pass


class GridFileNotFound(FileNotFoundError):
    pass


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


def get_yaml_information(yaml_file, grids_folder, check_pineappl=False):
    """Given a yaml_file, returns the corresponding dictionary.

    The dictionary contains all information and an extra field "paths"
    with all the grids to be loaded for the given dataset.
    Checks whether the grid is apfelcomb or pineappl:
    if check_pineappl is True this function will raise PineAPPLEquivalentNotKnown
    if a pineappl grid is not found.

    Parameters
    ----------
    yaml_file : Path
        path of the yaml file for the given dataset
    grids_folder : Path
        path of the theory folder where to find the grids

    Returns
    -------
    yaml_content: dict
        Metadata prepared for the FKTables
    paths: list(list(path))
        List (of lists) with all the grids that will need to be loaded
    """
    yaml_content = _load_yaml(yaml_file)

    if yaml_content.get("appl") and check_pineappl:
        # This might be useful to use the "legacy loader" when there is no actual pineappl available
        raise PineAPPLEquivalentNotKnown(yaml_content["target_dataset"])

    # Turn the operands and the members into paths (and check all of them exist)
    ret = []
    for operand in yaml_content["operands"]:
        tmp = []
        for member in operand:
            p = grids_folder / f"{member}.{ext}"
            if not p.exists():
                raise GridFileNotFound(f"Failed to find {p}")
            tmp.append(p)
        ret.append(tmp)

    # We have added a new operation, "NORM" so we need to play this game here:
    if yaml_content["operation"] == "NORM":
        # Case not yet considered in VP
        yaml_content["operation_function"] = "NULL"
    else:
        yaml_content["operation_function"] = yaml_content["operation"]

    return yaml_content, ret


def load_grids(theory_id, ds):
    """Load all grids (i.e. process scale) of a dataset.

    Parameters
    ----------
    theory_id : int
        theory id
    ds : str
        dataset name

    Returns
    -------
    grids : dict
        mapping basename to path
    """
    paths = configs.configs["paths"]
    try:
        _info, grids = get_yaml_information(
            paths["ymldb"] / f"{ds}.yaml", paths["grids"] / str(theory_id)
        )
    except GridFileNotFound:
        _info, grids = get_yaml_information(
            paths["ymldb"] / f"{ds}.yaml", paths["grids_common"]
        )
    # the list is still nested, so flatten
    grids = [grid for opgrids in grids for grid in opgrids]
    # then turn into a map name -> path
    grids = {grid.stem.rsplit(".", 1)[0]: grid for grid in grids}
    return grids

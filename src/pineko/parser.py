"""Interface to ymldb."""
# ATTENTION: this is a partial copy from
# https://github.com/NNPDF/nnpdf/blob/7cb96fc05ca2a2914bc1ccc864865e0ca4e66983/validphys2/src/validphys/pineparser.py

import yaml

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


def get_yaml_information(yaml_file, grids_folder):
    """Given a yaml_file, returns the corresponding dictionary and grids.

    The dictionary contains all information and we return an extra field
    with all the grids to be loaded for the given dataset.

    Parameters
    ----------
    yaml_file : pathlib.Path
        path of the yaml file for the given dataset
    grids_folder : pathlib.Path
        path of the grids folder

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
            if not p.exists():
                raise GridFileNotFound(f"Failed to find {p}")
            tmp.append(p)
        ret.append(tmp)

    return yaml_content, ret

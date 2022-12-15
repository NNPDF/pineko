"""Tools related to generation and managing of a pineko project."""

import os
import pathlib

from .configs import needed_keys


def set_up_project(configs):
    """Set up all the folders spelled up in the configs dictionary.

    Parameters
    ----------
    configs : dict
        configs dictionary containing all the paths to be set up
    """
    for path in configs["paths"]:
        if path == "root":
            continue
        if isinstance(configs["paths"][path], pathlib.Path):
            if configs["paths"][path].suffix == ".yaml":
                continue
            os.makedirs(configs["paths"][path], exist_ok=True)
        elif isinstance(configs["paths"][path], dict):
            for log_path in configs["paths"][path]:
                if isinstance(configs["paths"][path][log_path], pathlib.Path):
                    os.makedirs(configs["paths"][path][log_path], exist_ok=True)
                else:
                    raise TypeError(f"Not recognized entry {log_path} in configs")
        else:
            raise TypeError(f"Not recognized entry {path} in configs")


def check_folders(configs):
    """Check if all the folders spelled out in configs exist.

    Parameters
    ----------
    configs : dict
        configs dictionary containing all the paths to be checked
    """
    for key in needed_keys:
        if key not in configs["paths"]:
            raise ValueError(f"{key} not found in config file")
        if key == "operator_card_template":
            continue
        if not configs["paths"][key].exists():
            raise FileNotFoundError(
                f"Needed folder {configs['paths'][key]} does not exists"
            )
    if "logs" not in configs["paths"]:
        print("WARNING: logs folder is not spelled out in the config file")
    else:
        for key in configs["paths"]["logs"]:
            if not configs["paths"]["logs"][key].exists():
                raise FileNotFoundError(
                    f"Folder {configs['paths']['logs'][key]} does not exists"
                )
    return True

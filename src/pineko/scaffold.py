"""Tools related to generation and managing of a pineko project."""

import os
import pathlib

from .configs import needed_keys


def set_up_project(configs):
    """Set up all the folders spelled out in the configs dictionary.

    Parameters
    ----------
    configs : dict
        configs dictionary containing all the paths to be set up
    """
    for path in configs["paths"]:
        if path == "root" or path == "operator_card_template_name":
            continue
        if isinstance(configs["paths"][path], pathlib.Path):
            configs["paths"][path].mkdir(parents=True, exist_ok=True)
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
    Returns
    -------
    : tuple(bool, list, dict)
        tuple containing a bool which is True if the configuration is correct
        and False if not. The list contains the missing keys in the configuration
        file and the dictionary contains the folders that should exists but could
        not be found.
    """
    wrong_confs = []
    wrong_folders = {}
    for key in needed_keys:
        if key not in configs["paths"]:
            wrong_confs.append(key)
        else:
            if key == "operator_card_template_name":
                continue
            if not configs["paths"][key].exists():
                wrong_folders[key] = configs["paths"][key]
    if "logs" not in configs["paths"]:
        print("WARNING: logs folder is not spelled out in the config file")
    else:
        wrong_folders["logs"] = {}
        for key in configs["paths"]["logs"]:
            if not configs["paths"]["logs"][key].exists():
                wrong_folders["logs"][key] = configs["paths"]["logs"][key]
    success = (
        True
        if (len(wrong_confs) == 0 and list(wrong_folders.keys()) == ["logs"])
        else False
    )
    return (success, wrong_confs, wrong_folders)

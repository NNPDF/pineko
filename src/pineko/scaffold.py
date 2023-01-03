"""Tools related to generation and managing of a pineko project."""

import dataclasses
import os
import pathlib

from .configs import NEEDED_FILES, NEEDED_KEYS


@dataclasses.dataclass
class CheckResult:
    """Dataclass containing the results of a check. In particular it contains a bool that is True if the check has been successful, a list of missing entries in the configuration file and a dictionary containing all the folders that should exist but that could not be found."""

    success: bool
    confs: list
    folders: dict


def set_up_project(configs):
    """Set up all the folders spelled out in the configs dictionary.

    Parameters
    ----------
    configs : dict
        configs dictionary containing all the paths to be set up
    """
    for path in configs["paths"]:
        if path == "root" or path in NEEDED_FILES:
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
    : CheckResult
        object containing the result of the check
    """
    wrong_confs = []
    wrong_folders = {}
    for key in NEEDED_KEYS:
        if key not in configs["paths"]:
            wrong_confs.append(key)
        else:
            if key in NEEDED_FILES:
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
    success = len(wrong_confs) == 0 and list(wrong_folders.keys()) == ["logs"]
    return CheckResult(success, wrong_confs, wrong_folders)

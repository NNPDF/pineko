"""Tools related to generation and managing of a pineko project."""

import os
import pathlib


def set_up_project(configs):
    """Set up all the folders spelled up in the configs dictionary.

    Parameters
    ----------
    configs : dict
        configs dictionary containing all the paths to be setted up
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

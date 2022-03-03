# -*- coding: utf-8 -*-
import pathlib
import copy

import appdirs
import tomli

name = "pineko.toml"
"Name of the config while (wherever it is placed)"


# better to declare immediately the correct type
configs = {}
"Holds loaded configurations"


def add_scope(base, scope_id, scope):
    "Do not override."
    if scope_id not in base:
        base[scope_id] = scope
    else:
        for key, value in scope.items():
            if key not in base[scope_id]:
                base[scope_id] = value


def defaults(base_configs):
    """Provide additional defaults.

    Note
    ----
    The general rule is to never replace user provided input.
    """
    configs = copy.deepcopy(base_configs)

    configs = add_paths(configs)

    return configs


def add_paths(configs):
    for key in [
        "ymldb",
        "operator_cards",
        "grids",
        "grids_common",
        "opcard_template",
        "theory_cards",
        "fktables",
        "ekos",
    ]:
        if key not in configs["paths"]:
            raise ValueError(f"Configuration is missing a 'paths.{key}' key")
        elif pathlib.Path(configs["paths"][key]).anchor == "":
            configs["paths"][key] = configs["paths"]["root"] / configs["paths"][key]
        else:
            configs["paths"][key] = pathlib.Path(configs["paths"][key])

    if "logs" not in configs["paths"]:
        configs["paths"]["logs"] = {}

    for key in [
        "eko",
    ]:
        if key not in configs["paths"]["logs"]:
            configs["paths"]["logs"][key] = None
        elif pathlib.Path(configs["paths"][key]).anchor == "":
            configs["paths"]["logs"][key] = configs["paths"]["root"] / configs["paths"][key]
        else:
            configs["paths"]["logs"][key] = pathlib.Path(configs["paths"][key])

    return configs


def detect(path=None):
    paths = []

    if path is not None:
        path = pathlib.Path(path)
        paths.append(path)

    paths.append(pathlib.Path.cwd())
    paths.append(pathlib.Path.home())
    paths.append(pathlib.Path(appdirs.user_config_dir()))
    paths.append(pathlib.Path(appdirs.site_config_dir()))

    for p in paths:
        configs_file = p / name if p.is_dir() else p

        if configs_file.is_file():
            return configs_file

    raise FileNotFoundError("No configurations file detected.")


def load(path=None):
    try:
        path = detect(path)
    except FileNotFoundError:
        if path is None:
            return {"paths": {"root": pathlib.Path.cwd()}}
        else:
            print("Configuration path specified is not valid.")
            quit()

    with open(path, "rb") as fd:
        loaded = tomli.load(fd)

    if "paths" not in loaded:
        loaded["paths"] = {}
    if "root" not in loaded["paths"]:
        loaded["paths"]["root"] = pathlib.Path(path).parent

    return loaded

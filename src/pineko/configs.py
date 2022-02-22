# -*- coding: utf-8 -*-
import pathlib
import typing

import rich

name = "pineko.toml"
"Name of the config while (wherever it is placed)"


class Configurations:
    def __init__(self, dictionary=None):
        if isinstance(dictionary, Configurations):
            self._dict = dictionary._dict
        elif dictionary is None:
            self._dict = {}
        else:
            self._dict = dictionary

    def __repr__(self):
        return self._dict.__repr__()

    def __getattribute__(self, name) -> typing.Any:
        if name[0] == "_":
            return super().__getattribute__(name)

        value = self._dict[name]
        if isinstance(value, dict):
            value = Configurations(value)
        return value

    def __getitem__(self, key):
        return self.__getattribute__(key)

    def __setattribute__(self, name, value):
        self._dict[name] = value

    def __setitem__(self, key, value):
        if key[0] == "_":
            raise LookupError(
                "Elements with leading '_' can not be retrieved later, so you"
                f" can not set (attempted: '{key}')"
            )

        self._dict[key] = value

    def __contains__(self, item):
        return item in self._dict

    def _pprint(self):
        rich.print(self._dict)


# better to declare immediately the correct type
configs = Configurations()
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
    configs = Configurations(base_configs)

    configs = add_paths(configs)

    return Configurations(configs)


def add_paths(configs):
    for key, default in dict(grids="grids", ekos="ekos").items():
        if key not in configs.paths:
            configs.paths[key] = configs.paths.root / default
        elif pathlib.Path(configs.paths[key]).anchor == "":
            configs.paths[key] = configs.paths.root / configs.paths[key]
        else:
            configs.paths[key] = pathlib.Path(configs.paths[key])

    return configs

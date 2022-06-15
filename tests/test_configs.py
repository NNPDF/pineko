# -*- coding: utf-8 -*-
import pathlib

import pytest

import pineko

test_files = pathlib.Path(__file__).parents[0] / "test_files/"


def test_enhance_paths():
    # Testing with one missing key
    test_configs = {
        "paths": {
            "ymldb": pathlib.Path(""),
            "grids": pathlib.Path(""),
            "operator_card_template": pathlib.Path(""),
            "theory_cards": pathlib.Path(""),
            "fktables": pathlib.Path(""),
            "ekos": pathlib.Path(""),
            "root": pathlib.Path("/my/root/path/"),
            "logs": {"fk": pathlib.Path("my/fk/logs/")},
        },
    }
    with pytest.raises(ValueError):
        pineko.configs.enhance_paths(test_configs)
    test_configs["paths"]["operator_cards"] = pathlib.Path("my/ope/cards/")
    pineko.configs.enhance_paths(test_configs)
    assert test_configs["paths"]["operator_cards"] == pathlib.Path(
        "/my/root/path/my/ope/cards/"
    )
    assert test_configs["paths"]["logs"]["eko"] == None
    assert test_configs["paths"]["logs"]["fk"] == pathlib.Path(
        "/my/root/path/my/fk/logs/"
    )


def test_default():
    test_configs = {
        "paths": {
            "ymldb": pathlib.Path(""),
            "grids": pathlib.Path(""),
            "operator_cards": pathlib.Path("my/ope/cards/"),
            "operator_card_template": pathlib.Path(""),
            "theory_cards": pathlib.Path(""),
            "fktables": pathlib.Path(""),
            "ekos": pathlib.Path(""),
            "root": pathlib.Path("/my/root/path/"),
            "logs": {"fk": pathlib.Path("my/fk/logs/")},
        },
    }
    configs = pineko.configs.defaults(test_configs)
    assert configs["paths"]["ymldb"] == pathlib.Path("/my/root/path")


def test_detect():
    with pytest.raises(FileNotFoundError):
        pineko.configs.detect()
    conf_file = pineko.configs.detect(test_files)


def test_load():
    conf_file = pineko.configs.load(test_files)
    assert conf_file["paths"]["root"] == test_files
    assert conf_file["paths"]["grids"] == "data/grids"

# -*- coding: utf-8 -*-

import pathlib

import pytest

import pineko

test_files = pathlib.Path(__file__).parents[0] / "data_files/"


def benchmark_detect():
    with pytest.raises(FileNotFoundError):
        pineko.configs.detect()
    conf_file = pineko.configs.detect(test_files)


def benchmark_load():
    conf_file = pineko.configs.load(test_files)
    assert conf_file["paths"]["root"] == test_files
    assert conf_file["paths"]["grids"] == "data/grids/"

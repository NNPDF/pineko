# -*- coding: utf-8 -*-
import pathlib

import pytest

import pineko

test_files = pathlib.Path(__file__).parents[0] / "test_files/"


def test_write_operator_card_from_file(tmp_path):
    pine_path = test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    default_path = test_files / "data/operator_cards/_template.yaml"
    target_path = pathlib.Path(tmp_path / "test_operator.yaml")
    x_grid, q2_grid = pineko.evolve.write_operator_card_from_file(
        pine_path, default_path, target_path
    )
    wrong_pine_path = test_files / "data/grids/208/HERA_CC_318GEV_EM_wrong.pineappl.lz4"
    with pytest.raises(FileNotFoundError):
        x_grid, q2_grid = pineko.evolve.write_operator_card_from_file(
            wrong_pine_path, default_path, target_path
        )

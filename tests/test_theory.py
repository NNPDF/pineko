# -*- coding: utf-8 -*-
import pathlib

import pineko

theory_obj = pineko.theory.TheoryBuilder(208, ["HERACOMBCCEM"])
test_files = pathlib.Path(__file__).parents[0] / "test_files/"


def test_operators_cards_path():
    path = theory_obj.operator_cards_path
    assert path == pathlib.Path(test_files / "data/operator_cards/208")


def test_ekos_path():
    path = theory_obj.ekos_path()
    assert path == pathlib.Path(test_files / "data/ekos/208")


def test_fks_path():
    path = theory_obj.fks_path
    assert path == pathlib.Path(test_files / "data/fktables/208")


def test_grids_path():
    path = theory_obj.grids_path()
    assert path == pathlib.Path(test_files / "data/grids/208")


def test_load_grids():
    dataset_name = "HERACOMBCCEM"
    grids = theory_obj.load_grids(dataset_name)
    assert grids["HERA_CC_318GEV_EM_SIGMARED"] == pathlib.Path(
        test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    )


def test_inherit_grid(tmp_path):
    from_grid = theory_obj.grids_path()
    theory_obj.inherit_grid("TestGrid", from_grid, tmp_path)


def test_inherit_eko(tmp_path):
    from_eko = theory_obj.ekos_path()
    theory_obj.inherit_eko("TestEko", from_eko, tmp_path)

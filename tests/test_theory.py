# -*- coding: utf-8 -*-
import os
import pathlib

import pineko

theory_obj = pineko.theory.TheoryBuilder(208, ["LHCB_Z_13TEV_DIMUON"])
theory_obj_Hera = pineko.theory.TheoryBuilder(208, ["HERACOMBCCEM"])
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
    dataset_name = "LHCB_Z_13TEV_DIMUON"
    grids = theory_obj.load_grids(dataset_name)
    assert grids["LHCB_DY_13TEV_DIMUON"] == pathlib.Path(
        test_files / "data/grids/208/LHCB_DY_13TEV_DIMUON.pineappl.lz4"
    )


def test_inherit_grid(tmp_path):
    from_grid = theory_obj.grids_path()
    theory_obj.inherit_grid("TestGrid", from_grid, tmp_path)


def test_inherit_eko(tmp_path):
    from_eko = theory_obj.ekos_path()
    theory_obj.inherit_eko("TestEko", from_eko, tmp_path)


def test_opcard():
    grid_name = "LHCB_DY_13TEV_DIMUON"
    theory_obj.opcard(
        grid_name,
        pathlib.Path(test_files / "data/grids/208/LHCB_DY_13TEV_DIMUON.pineappl.lz4"),
    )
    op_path = pathlib.Path(
        test_files / theory_obj.operator_cards_path / "LHCB_DY_13TEV_DIMUON.yaml"
    )
    if os.path.exists(op_path):
        os.remove(op_path)
    else:
        raise ValueError("operator card not found")


def test_eko():
    grid_name = "LHCB_DY_13TEV_DIMUON"
    grid_path = pathlib.Path(theory_obj.grids_path() / (grid_name + ".pineappl.lz4"))
    base_configs = pineko.configs.load(test_files)
    pineko.configs.configs = pineko.configs.defaults(base_configs)
    tcard = pineko.theory_card.load(208)
    theory_obj.activate_logging(
        pathlib.Path(test_files / "logs/eko"),
        "208-LHCB_DY_13TEV_DIMUON.log",
        ["208-LHCB_DY_13TEV_DIMUON.log"],
    )
    theory_obj.opcard(grid_name, pathlib.Path(test_files / grid_path))

    theory_obj.eko(grid_name, grid_path, tcard)

    log_path = pathlib.Path(test_files / "logs/eko/208-LHCB_DY_13TEV_DIMUON.log")
    if os.path.exists(log_path):
        os.remove(log_path)
    else:
        raise ValueError("log file not found")
    op_path = pathlib.Path(
        test_files / theory_obj.operator_cards_path / "LHCB_DY_13TEV_DIMUON.yaml"
    )
    if os.path.exists(op_path):
        os.remove(op_path)
    else:
        raise ValueError("operator card not found")


def test_activate_logging():
    theory_obj.activate_logging(
        pathlib.Path(test_files / "logs/fk"), "test_log.log", ["test_log.log"]
    )
    log_path = pathlib.Path(test_files / "logs/fk/test_log.log")
    if os.path.exists(log_path):
        os.remove(log_path)
    else:
        raise ValueError("log file not found")


def test_fk():
    grid_name = "HERA_CC_318GEV_EM_SIGMARED"
    grid_path = pathlib.Path(
        theory_obj_Hera.grids_path() / (grid_name + ".pineappl.lz4")
    )
    base_configs = pineko.configs.load(test_files)
    pineko.configs.configs = pineko.configs.defaults(base_configs)
    tcard = pineko.theory_card.load(208)
    theory_obj_Hera.activate_logging(
        pathlib.Path(test_files / "logs/fk"),
        "208-HERA_CC_318GEV_EM_SIGMARED.log",
        ["208-HERA_CC_318GEV_EM_SIGMARED.log"],
    )
    theory_obj_Hera.opcard(grid_name, pathlib.Path(test_files / grid_path))

    theory_obj_Hera.fk(grid_name, grid_path, tcard, pdf=None)

    log_path = pathlib.Path(test_files / "logs/fk/208-HERA_CC_318GEV_EM_SIGMARED.log")
    if os.path.exists(log_path):
        os.remove(log_path)
    else:
        raise ValueError("log file not found")
    op_path = pathlib.Path(
        test_files
        / theory_obj_Hera.operator_cards_path
        / "HERA_CC_318GEV_EM_SIGMARED.yaml"
    )
    if os.path.exists(op_path):
        os.remove(op_path)
    else:
        raise ValueError("operator card not found")

    fk_path = pathlib.Path(
        test_files
        / theory_obj_Hera.fks_path
        / "HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    )
    if os.path.exists(fk_path):
        os.remove(fk_path)
    else:
        raise ValueError("fktable not found")
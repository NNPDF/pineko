# -*- coding: utf-8 -*-
import pathlib

from click.testing import CliRunner

from pineko.cli._base import command

test_files = pathlib.Path(__file__).parents[0] / "test_files/"


def test_check_cli():
    grid_path = pathlib.Path(
        test_files / "data/grids/208/LHCB_DY_13TEV_DIMUON.pineappl.lz4"
    )
    wrong_grid_path = pathlib.Path(
        test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    )
    eko_path = pathlib.Path(test_files / "data/ekos/208/LHCB_DY_13TEV_DIMUON.tar")
    runner = CliRunner()
    result = runner.invoke(
        command, ["check", "compatibility", str(grid_path), str(eko_path)]
    )
    assert "Success: grids are compatible" in result.output
    wrong_result = runner.invoke(
        command, ["check", "compatibility", str(wrong_grid_path), str(eko_path)]
    )
    assert (
        "Error: Q2 grid in pineappl grid and eko operator are NOT compatible!"
        in wrong_result.output
    )


def test_opcard_cli(tmp_path):
    grid_path = pathlib.Path(
        test_files / "data/grids/208/LHCB_DY_13TEV_DIMUON.pineappl.lz4"
    )
    default_card_path = pathlib.Path(test_files / "data/operator_cards/_template.yaml")
    target_path = pathlib.Path(tmp_path / "test_ope_card.yaml")
    runner = CliRunner()
    result = runner.invoke(
        command, ["opcard", str(grid_path), str(default_card_path), str(target_path)]
    )
    assert "Success" in result.output

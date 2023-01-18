import pathlib

from click.testing import CliRunner

from pineko.cli._base import command


def benchmark_check_cli(test_files):
    grid_path = pathlib.Path(
        test_files / "data/grids/400/HERA_NC_225GEV_EP_SIGMARED.pineappl.lz4"
    )
    wrong_grid_path = pathlib.Path(
        test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    )
    eko_path = pathlib.Path(test_files / "data/ekos/400/HERA_NC_225GEV_EP_SIGMARED.tar")
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
    wrong_scvar_res = runner.invoke(
        command, ["check", "scvar", str(grid_path), "wrong_string", "2", "0"]
    )
    assert "Invalid value for 'SCALE'" in wrong_scvar_res.output
    ren_res = runner.invoke(
        command, ["check", "scvar", str(grid_path), "ren", "2", "0"]
    )
    assert (
        "Success: grids contain renormalization scale variations for as"
        in ren_res.output
    )
    assert (
        "Success: grids contain renormalization scale variations for al"
        in ren_res.output
    )
    fact_res = runner.invoke(
        command, ["check", "scvar", str(grid_path), "fact", "2", "0"]
    )
    assert (
        "Success: grids contain factorization scale variations for as"
        in fact_res.output
    )
    assert (
        "Success: grids contain factorization scale variations for al"
        in fact_res.output
    )


def benchmark_opcard_cli(tmp_path, test_files):
    grid_path = pathlib.Path(
        test_files / "data/grids/208/LHCB_DY_13TEV_DIMUON.pineappl.lz4"
    )
    default_card_path = pathlib.Path(
        test_files / "data/operator_cards/208/_template.yaml"
    )
    thcard_path = pathlib.Path(test_files / "data" / "theory_cards" / "208.yaml")
    target_path = pathlib.Path(tmp_path / "test_ope_card.yaml")
    runner = CliRunner()
    result = runner.invoke(
        command,
        [
            "opcard",
            str(grid_path),
            str(default_card_path),
            str(target_path),
        ],
    )
    assert "Success" in result.output


def benchmark_compare_cli(lhapdf_path, test_files, test_pdf):
    grid_path = pathlib.Path(
        test_files / "data/grids/208/LHCB_DY_13TEV_DIMUON.pineappl.lz4"
    )
    fk_path = pathlib.Path(
        test_files / "data/fktables/208/LHCB_DY_13TEV_DIMUON.pineappl.lz4"
    )
    runner = CliRunner()
    with lhapdf_path(test_pdf):
        result = runner.invoke(
            command,
            ["compare", str(grid_path), str(fk_path), "2", "0", "NNPDF40_nlo_as_01180"],
        )
    assert "yll left" in result.output

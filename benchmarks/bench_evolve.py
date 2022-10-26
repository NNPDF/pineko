import pathlib

import eko
import eko.compatibility
import eko.output.legacy
import numpy as np
import pineappl
import pytest
import yaml
from eko import couplings as sc

import pineko


def benchmark_write_operator_card_from_file(tmp_path, test_files):
    pine_path = test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    default_path = test_files / "data/operator_cards/_template.yaml"
    target_path = pathlib.Path(tmp_path / "test_operator.yaml")

    # Load the theory card
    tcard = pineko.theory_card.load(208)

    x_grid, q2_grid = pineko.evolve.write_operator_card_from_file(
        pine_path, default_path, target_path, 1.0, tcard
    )

    # Load the operator card
    myopcard = yaml.safe_load(target_path.read_text(encoding="utf-8"))
    # Check if it contains all the information for eko
    assert np.allclose(myopcard["rotations"]["xgrid"], x_grid)
    assert np.allclose(myopcard["rotations"]["targetgrid"], x_grid)
    assert np.allclose(myopcard["rotations"]["inputgrid"], x_grid)
    assert np.allclose(myopcard["rotations"]["inputpids"], pineko.evolve.DEFAULT_PIDS)
    assert np.allclose(myopcard["rotations"]["targetpids"], pineko.evolve.DEFAULT_PIDS)

    wrong_pine_path = test_files / "data/grids/208/HERA_CC_318GEV_EM_wrong.pineappl.lz4"
    with pytest.raises(FileNotFoundError):
        x_grid, q2_grid = pineko.evolve.write_operator_card_from_file(
            wrong_pine_path, default_path, target_path, 1.0, tcard
        )


def benchmark_dglap(tmp_path):
    target_path = pathlib.Path(tmp_path / "test_operator.yaml")

    # In order to check if the operator card is enough for eko, let's compute the eko
    tcard = pineko.theory_card.load(208)
    # Load the opcard
    myopcard = yaml.safe_load(target_path.read_text(encoding="utf-8"))

    # I need smaller x and q grids in order to compute a small eko
    small_x_grid = [1.0e-6, 1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2, 1.0e-1, 1.0]
    small_q2_grid = [100.0]
    myopcard["xgrid"] = small_x_grid
    myopcard["targetgrid"] = small_x_grid
    myopcard["inputgrid"] = small_x_grid
    myopcard["Q2grid"] = small_q2_grid

    # upgrade cards layout
    newtcard, newocard = eko.compatibility.update(tcard, myopcard)

    _ = eko.run_dglap(theory_card=newtcard, operators_card=newocard)


def benchmark_evolve_grid(tmp_path, lhapdf_path, test_files, test_pdf):
    pine_path = test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    pinegrid = pineappl.grid.Grid.read(pine_path)
    eko_path = test_files / "data/ekos/208/HERA_CC_318GEV_EM_SIGMARED.tar"
    eko_op = eko.output.legacy.load_tar(eko_path)
    target_path = pathlib.Path(tmp_path / "test_fktable.pineappl.lz4")
    max_as = 1
    max_al = 0
    base_configs = pineko.configs.load(test_files)
    pineko.configs.configs = pineko.configs.defaults(base_configs)
    tcard = pineko.theory_card.load(208)
    new_tcard = eko.compatibility.update_theory(tcard)
    astrong = sc.Couplings.from_dict(new_tcard)
    assumptions = pineko.theory_card.construct_assumptions(tcard)
    with lhapdf_path(test_pdf):
        pineko.evolve.evolve_grid(
            pinegrid,
            eko_op,
            target_path,
            astrong,
            max_as,
            max_al,
            1.0,
            1.0,
            assumptions=assumptions,
            comparison_pdf="NNPDF40_nlo_as_01180",
        )

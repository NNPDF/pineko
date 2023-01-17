import pathlib

import eko
import eko.io.legacy
import numpy as np
import pineappl
import pytest
import yaml
from eko import couplings as sc

import pineko
import pineko.evolve
import pineko.theory_card


def benchmark_write_operator_card_from_file(tmp_path, test_files, test_configs):
    pine_path = test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    default_path = test_files / "data/operator_cards/208/_template.yaml"
    target_path = pathlib.Path(tmp_path / "test_operator.yaml")

    x_grid, _q2_grid = pineko.evolve.write_operator_card_from_file(
        pine_path, default_path, target_path, 1.0
    )

    # Load the operator card
    myopcard = yaml.safe_load(target_path.read_text(encoding="utf-8"))
    # Check if it contains all the information for eko
    assert np.allclose(myopcard["rotations"]["xgrid"], x_grid)
    assert np.allclose(myopcard["rotations"]["_targetgrid"], x_grid)
    assert np.allclose(
        myopcard["rotations"]["pids"], eko.basis_rotation.flavor_basis_pids
    )

    wrong_pine_path = test_files / "data/grids/208/HERA_CC_318GEV_EM_wrong.pineappl.lz4"
    with pytest.raises(FileNotFoundError):
        _ = pineko.evolve.write_operator_card_from_file(
            wrong_pine_path, default_path, target_path, 1.0
        )


def benchmark_dglap(tmp_path, test_files, test_configs):
    pine_path = test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    default_path = test_files / "data/operator_cards/208/_template.yaml"
    target_path = pathlib.Path(tmp_path / "test_operator.yaml")

    theory_id = 208
    tcard = pineko.theory_card.load(theory_id)
    # In order to check if the operator card is enough for eko, let's compute the eko
    # tcard = eko.compatibility.update_theory(pineko.theory_card.load(theory_id))
    # if "ModSV" not in tcard:
    #    tcard["ModSV"] = "expanded"

    pineko.evolve.write_operator_card_from_file(
        pine_path, default_path, target_path, 1.0
    )

    # Load the opcard
    myopcard = yaml.safe_load(target_path.read_text(encoding="utf-8"))

    # I need smaller x and q grids in order to compute a small eko
    small_x_grid = np.geomspace(1e-3, 1.0, 5)
    small_q2_grid = [100.0]
    myopcard["rotations"]["xgrid"] = small_x_grid
    myopcard["rotations"]["_targetgrid"] = small_x_grid
    myopcard["rotations"]["_inputgrid"] = small_x_grid
    myopcard["_mugrid"] = np.sqrt(small_q2_grid).tolist()
    legacy_class = eko.io.runcards.Legacy(tcard, myopcard)
    new_theory = legacy_class.new_theory
    new_op = eko.io.runcards.OperatorCard.from_dict(myopcard)

    # upgrade cards layout
    # newtcard, newocard = eko.compatibility.update(tcard, myopcard)

    # we are only interested in checking the configuration
    # instatianting a runner is mostly sufficient
    # TODO: speed up this step, and run a full run_dglap
    eko_path = pathlib.Path(tmp_path / "test_eko.tar")
    _ = eko.runner.solve(new_theory, new_op, eko_path)


def benchmark_evolve_grid(tmp_path, lhapdf_path, test_files, test_pdf):
    pine_path = test_files / "data/grids/400/HERA_NC_225GEV_EP_SIGMARED.pineappl.lz4"
    pinegrid = pineappl.grid.Grid.read(pine_path)
    eko_path = test_files / "data/ekos/400/HERA_NC_225GEV_EP_SIGMARED.tar"
    target_path = pathlib.Path(tmp_path / "test_fktable.pineappl.lz4")
    max_as = 3
    max_al = 0
    base_configs = pineko.configs.load(test_files)
    pineko.configs.configs = pineko.configs.defaults(base_configs)
    tcard = pineko.theory_card.load(400)
    assumptions = pineko.theory_card.construct_assumptions(tcard)
    with eko.EKO.edit(eko_path) as eko_op:
        with lhapdf_path(test_pdf):
            pineko.evolve.evolve_grid(
                pinegrid,
                eko_op,
                target_path,
                max_as,
                max_al,
                1.0,
                1.0,
                assumptions=assumptions,
                comparison_pdf="NNPDF40_nnlo_as_01180",
            )
            # check metadata is there - fixes https://github.com/NNPDF/pineko/issues/70
            fk = pineappl.fk_table.FkTable.read(target_path)
            assert "results_fk" in fk.key_values()

# -*- coding: utf-8 -*-
import pathlib

import eko
import pineappl
import pytest
from utils import lhapdf_path

import pineko

test_files = pathlib.Path(__file__).parents[0] / "data_files/"
test_pdf = pathlib.Path(__file__).parents[0] / "fakepdfs"


def benchmark_write_operator_card_from_file(tmp_path):
    pine_path = test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    default_path = test_files / "data/operator_cards/_template.yaml"
    target_path = pathlib.Path(tmp_path / "test_operator.yaml")
    x_grid, q2_grid = pineko.evolve.write_operator_card_from_file(
        pine_path, default_path, target_path, 1.0
    )
    wrong_pine_path = test_files / "data/grids/208/HERA_CC_318GEV_EM_wrong.pineappl.lz4"
    with pytest.raises(FileNotFoundError):
        x_grid, q2_grid = pineko.evolve.write_operator_card_from_file(
            wrong_pine_path, default_path, target_path, 1.0
        )


def benchmark_evolve_grid(tmp_path):
    pine_path = test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    pinegrid = pineappl.grid.Grid.read(pine_path)
    eko_path = test_files / "data/ekos/208/HERA_CC_318GEV_EM_SIGMARED.tar"
    eko_op = eko.output.Output.load_tar(eko_path)
    target_path = pathlib.Path(tmp_path / "test_fktable.pineappl.lz4")
    max_as = 1
    max_al = 0
    base_configs = pineko.configs.load(test_files)
    pineko.configs.configs = pineko.configs.defaults(base_configs)
    tcard = pineko.theory_card.load(208)
    assumptions = pineko.theory_card.construct_assumptions(tcard)
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
            comparison_pdf="NNPDF40_nlo_as_01180",
        )

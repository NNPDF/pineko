import pathlib

import eko
import numpy as np
import pineappl
import pytest

import pineko.check


def benchmark_check_grid_and_eko_compatible(test_files):
    grid = pineappl.grid.Grid.read(
        test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    )
    wrong_grid = pineappl.grid.Grid.read(
        test_files / "data/grids/208/NUTEV_CC_NU_FE_SIGMARED.pineappl.lz4"
    )
    ekoop = eko.output.Output.load_tar(
        test_files / "data/ekos/208/HERA_CC_318GEV_EM_SIGMARED.tar"
    )
    with pytest.raises(ValueError):
        pineko.check.check_grid_and_eko_compatible(wrong_grid, ekoop, 1.0)
    pineko.check.check_grid_and_eko_compatible(grid, ekoop, 1.0)
    ekoop.xgrid_reshape(targetgrid=[0.0001, 0.001, 0.1, 0.5, 1.0])
    with pytest.raises(ValueError):
        pineko.check.check_grid_and_eko_compatible(grid, ekoop, 1.0)

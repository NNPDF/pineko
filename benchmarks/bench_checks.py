import pathlib

import eko
import numpy as np
import pineappl
import pytest

import pineko.check
from pineko import ekompatibility


def benchmark_check_grid_and_eko_compatible(test_files):
    grid = pineappl.grid.Grid.read(
        test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    )
    wrong_grid = pineappl.grid.Grid.read(
        test_files / "data/grids/208/NUTEV_CC_NU_FE_SIGMARED.pineappl.lz4"
    )
    eko_filename = test_files / "data/ekos/208/HERA_CC_318GEV_EM_SIGMARED.tar"
    ekoop = ekompatibility.load(eko_filename)
    with pytest.raises(ValueError):
        pineko.check.check_grid_and_eko_compatible(wrong_grid, ekoop, 1.0)
    pineko.check.check_grid_and_eko_compatible(grid, ekoop, 1.0)
    eko.output.manipulate.xgrid_reshape(
        ekoop, targetgrid=eko.interpolation.XGrid([0.0001, 0.001, 0.1, 0.5, 1.0])
    )
    with pytest.raises(ValueError):
        pineko.check.check_grid_and_eko_compatible(grid, ekoop, 1.0)

# -*- coding: utf-8 -*-
import pathlib

import pineappl

import pineko


def benchmark_compare(lhapdf_path, test_files, test_pdf):
    pine_path = test_files / "data/grids/208/LHCB_DY_13TEV_DIMUON.pineappl.lz4"
    grid = pineappl.grid.Grid.read(pine_path)
    fk_path = test_files / "data/fktables/208/LHCB_DY_13TEV_DIMUON.pineappl.lz4"
    fk = pineappl.fk_table.FkTable.read(fk_path)
    pdf = "NNPDF40_nlo_as_01180"
    with lhapdf_path(test_pdf):
        comp_table = pineko.comparator.compare(grid, fk, 2, 0, pdf, 1.0, 1.0)
    errors = comp_table["permille_error"].values
    assertions = [er < 5.0 for er in errors]
    assert False not in assertions

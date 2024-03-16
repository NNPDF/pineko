import lhapdf
import numpy as np
import pineappl

from pineko import kfactor


def benchmark_kfactor_inclusion(test_files, tmp_path, test_pdf, lhapdf_path):
    fake_yaml_path = test_files / "data" / "yamldb" / "ATLAS_TTB_FAKE.yaml"
    pto_to_update = 3  # here we want to update NNLO
    pdf_name = "NNPDF40_nnlo_as_01180"
    kfactor.compute_k_factor_grid(
        test_files / "data" / "grids" / "400",
        test_files / "data" / "kfactors",
        fake_yaml_path,
        pto_to_update,
        target_folder=tmp_path,
    )
    pluskfactor_grid_path = tmp_path / "ATLAS_TTB_8TEV_LJ_TRAP.pineappl.lz4"
    with lhapdf_path(test_pdf):
        pdf = lhapdf.mkPDF(pdf_name)
    pluskfactor_grid = pineappl.grid.Grid.read(pluskfactor_grid_path)
    sv_list = [(1.0, 1.0)]  # Only ren sv have to be tested
    bin_number = pluskfactor_grid.bins()
    order_mask_nloQCD = pineappl.grid.Order.create_mask(
        pluskfactor_grid.orders(), 2, 0, True
    )
    order_mask_nnloQCD = pineappl.grid.Order.create_mask(
        pluskfactor_grid.orders(), 3, 0, True
    )
    to_test_res_nlo = pluskfactor_grid.convolute_with_one(
        2212,
        pdf.xfxQ2,
        pdf.alphasQ2,
        order_mask_nloQCD,
        np.array([], dtype=np.uint64),
        np.array([], dtype=bool),
        sv_list,
    ).reshape(bin_number, len(sv_list))
    to_test_res_nnlo = pluskfactor_grid.convolute_with_one(
        2212,
        pdf.xfxQ2,
        pdf.alphasQ2,
        order_mask_nnloQCD,
        np.array([], dtype=np.uint64),
        np.array([], dtype=bool),
        sv_list,
    ).reshape(bin_number, len(sv_list))
    centrals_kfactor, _ = kfactor.read_kfactor(
        test_files / "data" / "kfactors" / "CF_QCD_ATLAS_TTB_8TEV_LJ_TRAP.dat"
    )
    rtol = 1.0e-15
    for pred_ratio, kf in zip(
        to_test_res_nnlo.transpose()[0] / to_test_res_nlo.transpose()[0],
        centrals_kfactor,
    ):
        np.testing.assert_allclose(kf, pred_ratio, rtol=rtol)

import numpy as np
from eko.beta import beta_qcd

from pineko import scale_variations


def test_ren_sv_coeffs():
    np.testing.assert_allclose(
        scale_variations.ren_sv_coeffs(m=0, max_as=1, logpart=1, which_part=0, nf=5), 0
    )
    res_nf5 = scale_variations.ren_sv_coeffs(
        m=1, max_as=1, logpart=1, which_part=0, nf=5
    )
    res_nf4 = scale_variations.ren_sv_coeffs(
        m=1, max_as=1, logpart=1, which_part=0, nf=4
    )
    np.testing.assert_allclose(
        res_nf5 / res_nf4, beta_qcd((2, 0), 5) / beta_qcd((2, 0), 4)
    )
    exp_res = beta_qcd((2, 0), 5) * (1.0 / (4.0 * np.pi))
    np.testing.assert_allclose(
        scale_variations.ren_sv_coeffs(m=0, max_as=2, logpart=1, which_part=1, nf=5),
        exp_res,
    )


def test_compute_scale_factor():
    exp_res = beta_qcd((2, 0), 5) * (1.0 / (4.0 * np.pi))
    # Here we are saying that we need to rescale the order (1,0,0,0) which is
    # the NLO central, in order to obtain the order (2,0,1,0)
    np.testing.assert_allclose(
        scale_variations.compute_scale_factor(
            m=0, nec_order=(1, 0, 0, 0), to_construct_order=(2, 0, 1, 0), nf=5
        ),
        exp_res,
    )


def test_compute_orders_map():
    m = 0
    max_as = 1
    # In this case we expect only one necessary order
    exp_to_compute_ord = (1, 0, 1, 0)
    exp_nec_order = (0, 0, 0, 0)
    assert scale_variations.compute_orders_map(m, max_as, 0)[exp_to_compute_ord] == [
        exp_nec_order
    ]

import numpy as np

from pineko import kfactor


class fakealpha:
    def __init__(self, const_value):
        self.const_value = const_value

    def alphasQ2(self, q2):
        return self.const_value


def test_compute_scale_factor():
    const_value = 0.01180
    myfakealpha = fakealpha(const_value)
    fake_kfactor = [1.1, 1.2, 1.3]
    bin_index = 1
    np.testing.assert_allclose(
        kfactor.compute_scale_factor(
            0,
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            5.0**2,
            fake_kfactor,
            bin_index,
            myfakealpha,
        ),
        (1.0 / const_value) * (fake_kfactor[bin_index] - 1.0),
    )
    np.testing.assert_allclose(
        kfactor.compute_scale_factor(
            0,
            [0, 0, 0, 0],
            [2, 0, 0, 0],
            5.0**2,
            fake_kfactor,
            bin_index,
            myfakealpha,
        ),
        (1.0 / (const_value**2)) * (fake_kfactor[bin_index] - 1.0),
    )

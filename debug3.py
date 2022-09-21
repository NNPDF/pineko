# -*- coding: utf-8 -*-
import lhapdf
import numpy as np
import pineappl
import yadism
from eko import interpolation
from yadism.coefficient_functions.splitting_functions import lo, nlo
from yadism.esf.conv import convolute_operator

mode_g = not True

if mode_g:
    pdf = lhapdf.mkPDF("gonly", 0)
else:
    pdf = lhapdf.mkPDF("conly", 0)


b1 = pineappl.fk_table.FkTable.read("data/fktables/2205/test.pineappl.lz4")
c1 = pineappl.fk_table.FkTable.read("data/fktables/3205/test.pineappl.lz4")
out = yadism.output.Output.load_tar("test0.tar")

bb1 = b1.convolute_with_one(2212, pdf.xfxQ2)
cc1 = c1.convolute_with_one(2212, pdf.xfxQ2)

loc = np.array(
    [
        out["F2_light"][j].orders[(0, 0, 0, 0)][0][-3]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
nloc = np.array(
    [
        out["F2_light"][j].orders[(1, 0, 0, 0)][0][-3]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
nlog = np.array(
    [
        out["F2_light"][j].orders[(1, 0, 0, 0)][0][7]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
pqqc = np.array(
    [
        out["F2_light"][j].orders[(1, 0, 0, 1)][0][-3]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
pqgg = np.array(
    [
        out["F2_light"][j].orders[(1, 0, 0, 1)][0][7]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
interp = interpolation.InterpolatorDispatcher.from_dict(out, mode_N=False)
pqq = convolute_operator(lo.pqq(5), interp)[0]
pqg = convolute_operator(lo.pqg(5), interp)[0]
pgq = convolute_operator(nlo.pgq0(5), interp)[0]
pgg = convolute_operator(nlo.pgg0(5), interp)[0]

muf2 = 300.0 * 2.0**2
# a = pdf.alphasQ2(muf2)
a = 0.0078
if mode_g:
    f = np.array([pdf.xfxQ2(21, x, muf2) / x for x in out["interpolation_xgrid"]])
else:
    f = np.array([pdf.xfxQ2(4, x, muf2) / x for x in out["interpolation_xgrid"]])

# if mode_g:
#     # this yields 4/9 as it should
#     print((pqgg @ f)/(pqg.T @ f)/out["interpolation_xgrid"])
# else:
#     # this yields 22/90 ?!
#     print((pqqc @ f)/(pqq.T @ f)/out["interpolation_xgrid"])
# print(cc1/((loc + a*(nloc + pqqc)) @ f))

diff_grid = bb1 - cc1
if mode_g:
    diff_ana = a**2 * np.log(2.0**2) * ((nloc @ pqg.T @ f) + (nlog @ pgg.T @ f))
else:
    diff_ana = a**2 * np.log(2.0**2) * ((nloc @ pqq.T @ f) + (nlog @ pgq.T @ f))

print(diff_grid / diff_ana)

# -*- coding: utf-8 -*-
import lhapdf
import numpy as np
import matplotlib.pyplot as plt
import pineappl
import yadism
from eko import interpolation
from yadism.coefficient_functions.splitting_functions import lo, nlo
from yadism.esf.conv import convolute_operator

mode_g = True
mode_no_nlo = not True

if mode_g:
    pdf = lhapdf.mkPDF("gonly", 0)
else:
    pdf = lhapdf.mkPDF("conly", 0)

if mode_no_nlo:
    b1 = pineappl.fk_table.FkTable.read("data/fktables/2205/no-nlo-test.pineappl.lz4")
    c1 = pineappl.fk_table.FkTable.read("data/fktables/3205/no-nlo-test.pineappl.lz4")
else:
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
a = 0.011

if mode_no_nlo:
    nlog *= 0
    nloc *= 0

if mode_g:
    f = np.array([pdf.xfxQ2(21, x, muf2) / x for x in out["interpolation_xgrid"]])
else:
    f = np.array([pdf.xfxQ2(4, x, muf2) / x for x in out["interpolation_xgrid"]])

# if mode_g:
#     # this yields 4/9 as it should
#     print((pqgg @ f)/(pqg.T @ f)/out["interpolation_xgrid"])
# else:
#     # this yields 22/90 = 2*(1+4+1+4+1)/9/(2*5) as it should
#     print((pqqc @ f)/(pqq.T @ f)/out["interpolation_xgrid"])

# if mode_g:
#     print(cc1/((a*(nlog + pqgg*np.log(1./2.**2))) @ f))
# else:
#     print(cc1/((loc + a*(nloc + pqqc*np.log(1./2.**2))) @ f))

diff_grid = bb1 - cc1
# plt.plot(diff_grid, label="grid")
# nloc *= 1.9
# nlog *= 1.14
if mode_g:
    # plt.plot(a**2 * np.log(1./2.0**2) * ((nloc @ pqg.T @ f)), label="pqg")
    # plt.plot(a**2 * np.log(1./2.0**2) * ((nlog @ pgg.T @ f)), label="pgg")
    diff_ana = a**2 * np.log(1./2.0**2) * ((nloc @ pqg.T @ f) + (nlog @ pgg.T @ f))
else:
    # plt.plot(a**2 * np.log(1./2.0**2) * ((nloc @ pqq.T @ f)), label="pqq")
    # plt.plot(a**2 * np.log(1./2.0**2) * ((nlog @ pgq.T @ f)), label="pgq")
    diff_ana = a**2 * np.log(1./2.0**2) * ((nloc @ pqq.T @ f) + (nlog @ pgq.T @ f))
# plt.legend()
# plt.show()
# print(diff_grid/cc1)
# print(diff_grid)
print(diff_grid / diff_ana)

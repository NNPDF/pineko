# -*- coding: utf-8 -*-
import sys
import lhapdf
import numpy as np
import matplotlib.pyplot as plt
import pineappl
import yadism
from eko import interpolation
from eko import output
from ekomark.apply import apply_pdf

# from eko.output.struct import EKO
from yadism.coefficient_functions.splitting_functions import lo, nlo
from yadism.esf.conv import convolute_operator

# mode can be gluon only or charm only
mode_g = True
if len(sys.argv) > 1:
    fl = sys.argv[1].strip()
    if fl == "g":
        mode_g = True
    if fl == "c":
        mode_g = False

mode_no_nlo = True

# load respective PDF set
if mode_g:
    pdf = lhapdf.mkPDF("gonly", 0)
else:
    pdf = lhapdf.mkPDF("conly", 0)

# load FK tables
if mode_no_nlo:
    b1 = pineappl.fk_table.FkTable.read("data/fktables/2205/no-nlo-test.pineappl.lz4")
    c1 = pineappl.fk_table.FkTable.read("data/fktables/3205/no-nlo-test.pineappl.lz4")
else:
    b1 = pineappl.fk_table.FkTable.read("data/fktables/2205/test.pineappl.lz4")
    c1 = pineappl.fk_table.FkTable.read("data/fktables/3205/test.pineappl.lz4")
out = yadism.output.Output.load_tar("test0.tar")

# compute predictions from FK
bb1 = b1.convolute_with_one(2212, pdf.xfxQ2)
cc1 = c1.convolute_with_one(2212, pdf.xfxQ2)

# load ingredients from yadism
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

# compute splitting functions
interp = interpolation.InterpolatorDispatcher.from_dict(out, mode_N=False)
pqq = convolute_operator(lo.pqq(5), interp)[0]
pqg = convolute_operator(lo.pqg(5), interp)[0]  # / 10 # * 55 / 100
pgq = convolute_operator(nlo.pgq0(5), interp)[0]
pgg = convolute_operator(nlo.pgg0(5), interp)[0]

muf2 = 300.0 * 2.0**2
# a = pdf.alphasQ2(muf2)
a = 0.011
L = np.log(1.0 / 2.0**2)

if mode_no_nlo:
    nlog *= 0
    nloc *= 0

# compute PDFs
if mode_g:
    f = np.array([pdf.xfxQ2(21, x, muf2) / x for x in out["interpolation_xgrid"]])
else:
    f = np.array([pdf.xfxQ2(4, x, muf2) / x for x in out["interpolation_xgrid"]])

# check yadism SV is proportional splitting functions
# print("check yadism SV")
# if mode_g:
#     # this yields 4/9 as it should
#     print((pqgg @ f)/(pqg.T @ f)/out["interpolation_xgrid"])
# else:
#     # this yields 22/90 = 2*(1+4+1+4+1)/9/(2*5)
#     print((pqqc @ f)/(pqq.T @ f)/out["interpolation_xgrid"])

# extract a by comparing C against yadism
# print("check C result")
# if mode_g:
#     print(cc1/((a*(nlog + pqgg*L)) @ f))
# else:
#     print(cc1/((loc + a*(nloc + pqqc*L)) @ f))

# construct K
Kqq = np.eye(len(out["interpolation_xgrid"])) + a * L * pqq.T
Kgg = np.eye(len(out["interpolation_xgrid"])) + a * L * pgg.T
Kqg = a * L * pqg.T
Kgq = a * L * pgq.T

# check B EKO is K
print("check B EKO result")
ekob = output.Output.load_tar("data/ekos/2205/test.tar")
fb = apply_pdf(ekob, pdf)
if mode_g:
    gb = Kgg @ f
    cb = Kqg @ f
else:
    gb = Kgq @ f
    cb = Kqq @ f
print(fb[300.0]["pdfs"][21] / gb)
print(fb[300.0]["pdfs"][4] / cb)

# check C EKO is identity
# print("check C EKO result")
# ekoc = output.Output.load_tar("data/ekos/3205/test.tar")
# fc = apply_pdf(ekoc, pdf)
# if mode_g:
#     print(fc[2.**2 * 300.]["pdfs"][21]/f)
#     print(fc[2.**2 * 300.]["pdfs"][4] - np.zeros_like(f))
# else:
#     print(fc[2.**2 * 300.]["pdfs"][4]/f)
#     print(fc[2.**2 * 300.]["pdfs"][21] - np.zeros_like(f))

# check B result
print("check B result")
if mode_g:
    print(bb1 / (((loc + a * nloc) @ Kqg + (a * nlog) @ Kgg) @ f))
else:
    print(bb1 / (((loc + a * nloc) @ Kqq + (a * nlog) @ Kgq) @ f))

diff_grid = bb1 - cc1
# plt.plot(diff_grid, label="grid")
# nloc *= 1.9
# nlog *= 1.14
if mode_g:
    # plt.plot(a**2 * L * ((nloc @ pqg.T @ f)), label="pqg")
    # plt.plot(a**2 * L * ((nlog @ pgg.T @ f)), label="pgg")
    diff_ana = a**2 * L * ((nloc @ pqg.T @ f) + (nlog @ pgg.T @ f))
else:
    # plt.plot(a**2 * L * ((nloc @ pqq.T @ f)), label="pqq")
    # plt.plot(a**2 * L * ((nlog @ pgq.T @ f)), label="pgq")
    diff_ana = a**2 * L * ((nloc @ pqq.T @ f) + (nlog @ pgq.T @ f))
# plt.legend()
# plt.show()
# print(diff_grid/cc1)
# print(diff_grid)
# print(diff_grid / diff_ana)

# -*- coding: utf-8 -*-
import sys
import lhapdf
import numpy as np
import matplotlib.pyplot as plt
import pineappl
import yadism
import yaml
import eko
from eko import interpolation
from eko import output
from eko import strong_coupling as sc
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
if len(sys.argv) > 2:
    mode_no_nlo = sys.argv[1].strip().lower() == "nlo"

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
los = np.array(
    [
        out["F2_light"][j].orders[(0, 0, 0, 0)][0][-4]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
nloc = np.array(
    [
        out["F2_light"][j].orders[(1, 0, 0, 0)][0][-3]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
nlos = np.array(
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
pqg = convolute_operator(lo.pqg(5), interp)[0] / 10  # * 55 / 100
pgq = convolute_operator(nlo.pgq0(5), interp)[0]
pgg = convolute_operator(nlo.pgg0(5), interp)[0]

q2 = 300.0
muf2 = q2 * 2.0**2
# load theory card
with open("data/theory_cards/2205.yaml") as fd:
    tc = yaml.safe_load(fd)
astrong = sc.StrongCoupling.from_dict(tc)
# actually, there are two alpha_s values in the game!
ac = astrong.a_s(muf2)
ab = astrong.a_s(q2)
L = np.log(1.0 / 2.0**2)

# shut yadism references down
if mode_no_nlo:
    nlog *= 0
    nloc *= 0
    nlos *= 0

# create joint quark terms
loq = 2 * (3 * los + 2 * loc)
nloq = 2 * (3 * nlos + 2 * nloc)

# construct K
Kqq = np.eye(len(out["interpolation_xgrid"])) + ac * L * pqq.T
Kgg = np.eye(len(out["interpolation_xgrid"])) + ac * L * pgg.T
Kqg = ac * L * pqg.T
Kgq = ac * L * pgq.T

# compute PDFs
if mode_g:
    f = np.array([pdf.xfxQ2(21, x, muf2) / x for x in out["interpolation_xgrid"]])
else:
    f = np.array([pdf.xfxQ2(4, x, muf2) / x for x in out["interpolation_xgrid"]])

# check yadism SV is proportional splitting functions
# print("check yadism SV")
# if mode_g:
#     print((pqgg @ f)/(loq @ pqg.T @ f))
# else:
#     print((pqqc @ f)/(loc @ pqq.T @ f))

# extract a by comparing C against yadism
# print("check C result")
# if mode_g:
#     print(cc1/((ac*(nlog + pqgg*L)) @ f))
# else:
#     print(cc1/((loc + ac*(nloc + pqqc*L)) @ f))

# check B EKO is K
# print("check B EKO result")
# ekob = output.Output.load_tar("data/ekos/2205/test.tar")
# fb = apply_pdf(ekob, pdf)
# if mode_g:
#     gb = Kgg @ f
#     cb = Kqg @ f
# else:
#     gb = Kgq @ f
#     cb = Kqq @ f
# print(fb[300.0]["pdfs"][21] / gb)
# print(fb[300.0]["pdfs"][4] / cb)

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
# print("check B result")
# if mode_g:
#     print(bb1 / (((loq + ab * nloq) @ Kqg + (ab * nlog) @ Kgg) @ f))
#     plt.plot(bb1)
#     plt.plot((((loq + ab * nloq) @ Kqg + (ab * nlog) @ Kgg) @ f))
# else:
#     print(bb1 / (((loc + ab * nloc) @ Kqq + (ab * nlog) @ Kgq) @ f))
# plt.show()

# check difference between B and C
print("check B - C")
diff_grid = bb1 - cc1
# plt.plot(bb1, label="b-grid")
# plt.plot(cc1, label="c-grid")
# nloc *= 1.9
# nlog *= 1.14
if mode_g:
    # plt.plot(a**2 * L * ((nloc @ pqg.T @ f)), label="pqg")
    # plt.plot(a**2 * L * ((nlog @ pgg.T @ f)), label="pgg")
    diff_ana = (nlog * (ab - ac) + ac * ab * L * ((nloq @ pqg.T) + (nlog @ pgg.T))) @ f
else:
    # plt.plot(a**2 * L * ((nloc @ pqq.T @ f)), label="pqq")
    # plt.plot(a**2 * L * ((nlog @ pgq.T @ f)), label="pgq")
    diff_ana = (nloc * (ab - ac) + ab * ac * L * ((nloc @ pqq.T) + (nlog @ pgq.T))) @ f
# print(diff_grid/cc1)
print(bb1 / cc1)
print(diff_grid / diff_ana)
plt.plot(diff_grid, label="grid")
plt.plot(diff_ana, label="ana")
# plt.plot((diff_grid/bb1-1)*100, label="rel err. diff to b")
# plt.plot(diff_grid/diff_ana, label="ratio")
plt.legend()
plt.show()

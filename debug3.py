import sys
from enum import Enum

import eko
import lhapdf
import matplotlib.pyplot as plt
import numpy as np
import pineappl
import yadism
import yaml
from eko import compatibility
from eko import couplings as sc
from eko import interpolation, output
from eko.beta import beta_qcd_as2
from eko.output import legacy
from ekomark.apply import apply_pdf

# from eko.output.struct import EKO
from yadism.coefficient_functions.splitting_functions import lo, nlo
from yadism.esf.conv import convolute_operator

from pineko import ekompatibility

# mode can be gluon only or charm only
mode_g = True
if len(sys.argv) > 1:
    fl = sys.argv[1].strip().lower()
    if fl == "g":
        mode_g = True
    if fl == "c":
        mode_g = False

# order mode
class Order(Enum):
    nonlo = 0
    nlo = 1
    nnlo = 2


order_mode = Order.nonlo
if len(sys.argv) > 2:
    om = sys.argv[2].strip().lower()
    if om == "nlo":
        order_mode = Order.nlo
    elif om == "nnlo":
        order_mode = Order.nnlo

signed = False
if len(sys.argv) > 3:
    sig = sys.argv[3].strip().lower()
    if sig == "signed":
        signed = True

# load respective PDF set
if order_mode == Order.nnlo:
    if mode_g:
        pdf = lhapdf.mkPDF("gonly_nnlo", 0)
    else:
        pdf = lhapdf.mkPDF("conly_nnlo", 0)
else:
    if mode_g:
        pdf = lhapdf.mkPDF("gonly", 0)
    else:
        pdf = lhapdf.mkPDF("conly", 0)
# load FK tables
if order_mode == Order.nonlo:
    b1 = pineappl.fk_table.FkTable.read("data/fktables/2205/no-nlo-test.pineappl.lz4")
    c1 = pineappl.fk_table.FkTable.read("data/fktables/3205/no-nlo-test.pineappl.lz4")
elif order_mode == Order.nlo:
    b1 = pineappl.fk_table.FkTable.read("data/fktables/2205/test.pineappl.lz4")
    c1 = pineappl.fk_table.FkTable.read("data/fktables/3205/test.pineappl.lz4")
elif order_mode == Order.nnlo:
    # 2405: bugged version
    # 2505: the minus sign is globally in K
    # 2605: the minus sign is in the definition of the gamma
    # 2705: the minus sign is in the definition of L
    # 2805: the minus sign is in the definition of beta0 and in the global K
    # b1 = pineappl.fk_table.FkTable.read("data/fktables/2405/test-nnlo.pineappl.lz4") #this is the one with the wrong sign
    c1 = pineappl.fk_table.FkTable.read("data/fktables/3405/test-nnlo.pineappl.lz4")
    b1 = pineappl.fk_table.FkTable.read("data/fktables/2505/test-nnlo.pineappl.lz4")
    # b1 = pineappl.fk_table.FkTable.read(
    #    "data/fktables/2605/test-nnlo.pineappl.lz4"
    # )
    # b1 = pineappl.fk_table.FkTable.read(
    #    "data/fktables/2705/test-nnlo.pineappl.lz4"
    # )
    # b1 = pineappl.fk_table.FkTable.read(
    #    "data/fktables/2805/test-nnlo.pineappl.lz4"
    # )
out = yadism.output.Output.load_tar("../test0.tar")
# compute predictions from FK
bb1 = b1.convolute_with_one(2212, pdf.xfxQ2)
cc1 = c1.convolute_with_one(2212, pdf.xfxQ2)

# load ingredients from yadism ---
# LO
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
# NLO
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
# NLO SV
nlosvc = np.array(
    [
        out["F2_light"][j].orders[(1, 0, 0, 1)][0][-3]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
nlosvg = np.array(
    [
        out["F2_light"][j].orders[(1, 0, 0, 1)][0][7]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
# NNLO
nnloc = np.array(
    [
        out["F2_light"][j].orders[(2, 0, 0, 0)][0][-3]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
nnlos = np.array(
    [
        out["F2_light"][j].orders[(2, 0, 0, 0)][0][-3]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
nnlog = np.array(
    [
        out["F2_light"][j].orders[(2, 0, 0, 0)][0][7]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
# NNLO SV
nnlosv1c = np.array(
    [
        out["F2_light"][j].orders[(2, 0, 0, 1)][0][-3]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
nnlosv1g = np.array(
    [
        out["F2_light"][j].orders[(2, 0, 0, 1)][0][7]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
nnlosv2c = np.array(
    [
        out["F2_light"][j].orders[(2, 0, 0, 2)][0][-3]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)
nnlosv2g = np.array(
    [
        out["F2_light"][j].orders[(2, 0, 0, 2)][0][7]
        for j in range(len(out["interpolation_xgrid"]))
    ]
)

# compute splitting functions
mygrid = eko.interpolation.XGrid(out["interpolation_xgrid"])
interp = interpolation.InterpolatorDispatcher(
    mygrid, out["interpolation_polynomial_degree"], mode_N=False
)
pqq0 = convolute_operator(lo.pqq(5), interp)[0].T
pqg0 = convolute_operator(lo.pqg(5), interp)[0].T / 10  # * 55 / 100
pgq0 = convolute_operator(nlo.pgq0(5), interp)[0].T
pgg0 = convolute_operator(nlo.pgg0(5), interp)[0].T
pqq1 = convolute_operator(nlo.pqq1(5), interp)[0].T
# pgg1 = convolute_operator(nlo.pgg1(5), interp)[0].T
pgg1 = pgg0  # just to have something, to be substituted with the correct one
pqg1 = convolute_operator(nlo.pqg1(5), interp)[0].T
# pgq1 = convolute_operator(nlo.pgq1(5), interp)[0].T
pgq1 = pgq0  # just to have something, to be substituted with the correct one
beta0I = beta_qcd_as2(5) * np.eye(pqg0.shape[0])
q2 = 300.0
muf2 = q2 * 2.0**2
# load theory card
if order_mode == Order.nnlo:
    with open("data/theory_cards/2405.yaml") as fd:
        old_tc = yaml.safe_load(fd)
else:
    with open("data/theory_cards/2205.yaml") as fd:
        old_tc = yaml.safe_load(fd)
tc = eko.compatibility.update_theory(old_tc)
astrong = sc.Couplings.from_dict(tc)
# actually, there are two alpha_s values in the game!
# ac = astrong.a_s(muf2)
ab = astrong.a_s(q2)
L = np.log(1.0 / 2.0**2)

# shut yadism references down
if order_mode == Order.nonlo:
    nlog *= 0
    nloc *= 0
    nlos *= 0
if order_mode == Order.nonlo or order_mode == Order.nlo:
    nnlog *= 0
    nnloc *= 0
    nnlos *= 0

# create joint quark terms
loq = 2 * (3 * los + 2 * loc)
nloq = 2 * (3 * nlos + 2 * nloc)
nnloq = 2 * (3 * nnlos + 2 * nnloc)

# construct K
Kqq = np.eye(len(out["interpolation_xgrid"])) + ab * L * pqq0
Kgg = np.eye(len(out["interpolation_xgrid"])) + ab * L * pgg0
Kqg = ab * L * pqg0
Kgq = ab * L * pgq0
# We believe to have a minus sign problem so:
if signed:
    Kqg = -Kqg
    Kgq = -Kgq
    Kqq = np.eye(len(out["interpolation_xgrid"])) - ab * L * pqq0
    Kgg = np.eye(len(out["interpolation_xgrid"])) - ab * L * pgg0


# compute PDFs
if mode_g:
    f = np.array([pdf.xfxQ2(21, x, muf2) / x for x in out["interpolation_xgrid"]])
else:
    f = np.array([pdf.xfxQ2(4, x, muf2) / x for x in out["interpolation_xgrid"]])
# Todo: Correct this part at nnlo
def check_yad_sv(plot=False):
    """Check if yadism SV is proportional to splitting functions."""
    print("check yadism SV")
    # collect data
    ops = {
        "nlosv": None,
        "nnlosv1": None,
        "nnlosv2": None,
    }
    if mode_g:
        ops["nlosv"] = (nlosvg, loq @ pqg0)
        ops["nnlosv1"] = (
            nnlosv1g,
            loq @ pqg1 + nlog @ pgg0 + nloq @ pqg0,
        )
        ops["nnlosv2"] = (
            nnlosv2g,
            (1.0 / 2.0) * loq @ pqq0 @ pqg0
            + (-beta0) * (1.0 / 2.0) * loq @ pqq0
            + (1.0 / 2.0) * (loq @ pqg0 @ pgg0)
            + (-beta0) * (1.0 / 2.0) * (loq @ pqg0),
        )
    else:
        ops["nlosv"] = (nlosvc, loc @ pqq0)
        ops["nnlosv1"] = (
            nnlosv1c,
            loc @ pqq1 + nloc @ pqq0 + nlog @ pgq0,
        )
        ops["nnlosv2"] = (
            nnlosv2c,
            1.0 / 2.0 * loq @ pqg0 @ pgq0 + 1.0 / 2.0 * (loc @ pqq0 @ (pqq0 + beta0I)),
        )
    # print check
    for k, v in ops.items():
        if v is None:
            continue
        print("ratio", k)
        print((v[0] @ f) / (v[1] @ f))
        # show actual curves?
        if plot:
            plt.title(f"{k}@{pdf.set().name}")
            plt.plot((v[0] @ f), label="yad")
            plt.plot((v[1] @ f), label="ana")
            plt.legend()
            plt.show()


# check_yad_sv(True)

# extract a by comparing C against yadism
def check_c_res():
    print("check C result")
    if mode_g:
        if order_mode == Order.nlo or order_mode == Order.nonlo:
            op = ab * (nlog + nlosvg * L)
        if order_mode == Order.nnlo:
            op_nlo = ab * (nlog + nlosvg * L)
            op_nnlo = ab * ab * (nnlog + L * nnlosv1g + L * L * nnlosv2g)
            op = op_nlo + op_nnlo
    else:
        if order_mode == Order.nlo or order_mode == Order.nonlo:
            op = loc + ab * (nloc + nlosvc * L)
        if order_mode == Order.nnlo:
            op_nlo = loc + ab * (nloc + nlosvc * L)
            op_nnlo = ab * ab * (nnlog + L * nnlosv1c + L * L * nnlosv2c)
            op = op_nlo + op_nnlo

    print(cc1 / (op @ f))


check_c_res()
# check B EKO is K
print("check B EKO result")
if order_mode == Order.nnlo:
    ekob = output.EKO.load("data/ekos/2405/test-nnlo.tar")
else:
    ekob = legacy.load_tar("data/ekos/2205/test.tar")
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
print("check C EKO result")
if order_mode == Order.nnlo:
    ekoc = output.EKO.load("data/ekos/3405/test-nnlo.tar")
else:
    ekoc = legacy.load_tar("data/ekos/3205/test.tar")
fc = apply_pdf(ekoc, pdf)
if mode_g:
    print(fc[2.0**2 * 300.0]["pdfs"][21] / f)
    print(fc[2.0**2 * 300.0]["pdfs"][4] - np.zeros_like(f))
else:
    print(fc[2.0**2 * 300.0]["pdfs"][4] / f)
    print(fc[2.0**2 * 300.0]["pdfs"][21] - np.zeros_like(f))

# check B result
print("check B result")
if mode_g:
    print(bb1 / (((loq + ab * nloq) @ Kqg + (ab * nlog) @ Kgg) @ f))
    # plt.plot(bb1, label="b-fk")
    # plt.plot(((loq + ab * nloq) @ (Kqg) + (ab * nlog) @ (Kgg)) @ f, label="ana_pred")
else:
    print(bb1 / (((loc + ab * nloc) @ Kqq + (ab * nlog) @ Kgq) @ f))
    # plt.plot(bb1, label="b-fk")
    # plt.plot(((loc + ab * nloc) @ Kqq + (ab * nlog) @ Kgq) @ f, label="ana_pred")
# plt.legend()
# plt.show()
# check difference between B and C
print("check B - C")
if order_mode == Order.nlo or order_mode == Order.nnlo:
    diff_grid = bb1 - cc1
    plt.plot(bb1[3:], label="b-grid")
    plt.plot(cc1[3:], label="c-grid")
    plt.legend()
    plt.show()
    if mode_g:
        # plt.plot(ab**2 * L * ((nloc @ pqg0 @ f)), label="pqg0")
        # plt.plot(ab**2 * L * ((nlog @ pgg0 @ f)), label="pgg0")
        if order_mode == Order.nlo:
            diff_ana = (ab * ab * L * ((nloq @ pqg0) + (nlog @ pgg0))) @ f
            if signed:
                diff_ana = (
                    -2 * ab * L * (loq @ pqg0)
                    - ab * ab * L * ((nloq @ pqg0) + (nlog @ pgg0))
                ) @ f
        else:
            pgg1 = pgg0
            nnlomix = (
                nlog @ pgg0 @ (pgg0 - beta0I)
                + nlog @ pgq0 @ (pqg0 - beta0I)
                + nloq @ pqq0 @ (pqg0 - beta0I)
                + nloq @ pqg0 @ (pgg0 - beta0I)
            )
            nnlomix2 = (
                nnlog @ pgg0 @ (pgg0 - beta0I)
                + nnlog @ pgq0 @ (pqg0 - beta0I)
                + nnloq @ pqq0 @ (pqg0 - beta0I)
                + nnloq @ pqg0 @ (pgg0 - beta0I)
            )
            diff_ana_nnlo = (
                (ab * ab * ab)
                * (
                    L
                    * ((nloq @ pqg1) + (nlog @ pgg1) + (nnlog @ pgg0) + (nnloq @ pqg0))
                    + L * L * ((-1.0 / 2.0) * nnlomix)
                )
                + (
                    ab
                    * ab
                    * ab
                    * ab
                    * (
                        L * ((nnlog @ pgg1) + (nnloq @ pqg1))
                        + L * L * ((-1.0 / 2.0) * (nnlomix2))
                    )
                )
            ) @ f
            diff_ana = diff_ana_nnlo
            if signed:
                diff_ana_nlo = (
                    -2 * ab * L * (loq @ pqg0)
                    - ab * ab * L * ((nloq @ pqg0) + (nlog @ pgg0))
                ) @ f
                diff_ana_nnlo = 0.0
                diff_ana = diff_ana_nlo + diff_ana_nnlo
    else:
        # plt.plot(a**2 * L * ((nloc @ pqq0 @ f)), label="pqq0")
        # plt.plot(a**2 * L * ((nlog @ pgq0 @ f)), label="pgq0")
        if order_mode == Order.nlo:
            diff_ana = (ab * ab * L * ((nloc @ pqq0) + (nlog @ pgq0))) @ f
            if signed:
                diff_ana = (
                    -2 * ab * L * (loc @ pqq0)
                    - ab * ab * L * ((nloc @ pqq0) + (nlog @ pgq0))
                ) @ f
        else:
            pgq1 = pgq0
            nnlomix = (
                nlog @ pgg0 @ (pgq0 - beta0I)
                + nlog @ pgq0 @ (pqq0 - beta0I)
                + nloq @ pqq0 @ (pqq0 - beta0I)
                + nloq @ pqg0 @ (pgq0 - beta0I)
            )
            nnlomix2 = (
                nnlog @ pgg0 @ (pgq0 - beta0I)
                + nnlog @ pgq0 @ (pqq0 - beta0I)
                + nnloq @ pqq0 @ (pqq0 - beta0I)
                + nnloq @ pqg0 @ (pgq0 - beta0I)
            )
            diff_ana_nnlo = (
                (ab * ab * ab)
                * (
                    L
                    * ((nloq @ pqq1) + (nlog @ pgq1) + (nnlog @ pgq0) + (nnloq @ pqq0))
                    + L * L * ((-1.0 / 2.0) * nnlomix)
                )
                + (ab * ab * ab * ab)
                * (
                    L * ((nnlog @ pgq1) + (nnloq @ pqq1))
                    + L * L * ((-1.0 / 2.0) * (nnlomix2))
                )
            ) @ f
            diff_ana = diff_ana_nnlo
            if signed:
                diff_ana_nlo = (
                    -2 * ab * L * (loc @ pqq0)
                    - ab * ab * L * ((nloc @ pqq0) + (nlog @ pgq0))
                ) @ f
                diff_ana_nnlo = 0.0
                diff_ana = diff_ana_nlo + diff_ana_nnlo
    print((diff_grid[3:] / bb1[3:]) * 100)
    print((diff_grid[3:] / cc1[3:]) * 100)
    print(((diff_grid[3:] / diff_ana[3:]) - 1.0) * 100)
    plt.plot(diff_grid[3:], label="grid")
    plt.plot(diff_ana[3:], label="ana")
    plt.legend()
    plt.show()
    plt.plot(((diff_grid[3:] / diff_ana[3:]) - 1.0) * 100, label="ratio")
    plt.legend()
    plt.show()

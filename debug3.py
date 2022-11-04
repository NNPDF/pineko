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
from eko.beta import beta_qcd_as2  # find the substitute
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

# load respective PDF set
if mode_g:
    pdf = lhapdf.mkPDF("gonly", 0)
else:
    pdf = lhapdf.mkPDF("conly", 0)
# load FK tables
if order_mode == Order.nonlo:
    b1 = pineappl.fk_table.FkTable.read(
        "../data/fktables/2205/no-nlo-test.pineappl.lz4"
    )
    c1 = pineappl.fk_table.FkTable.read(
        "../data/fktables/3205/no-nlo-test.pineappl.lz4"
    )
elif order_mode == Order.nlo:
    b1 = pineappl.fk_table.FkTable.read("../data/fktables/2205/test.pineappl.lz4")
    c1 = pineappl.fk_table.FkTable.read("../data/fktables/3205/test.pineappl.lz4")
elif order_mode == Order.nnlo:
    b1 = pineappl.fk_table.FkTable.read("../data/fktables/2205/test-nnlo.pineappl.lz4")
    c1 = pineappl.fk_table.FkTable.read("../data/fktables/3205/test-nnlo.pineappl.lz4")
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
pqg1 = convolute_operator(nlo.pqg1(5), interp)[0].T
beta0I = beta_qcd_as2(5) * np.eye(pqg0.shape[0])

q2 = 300.0
muf2 = q2 * 2.0**2
# load theory card
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
minus_sign = True
if minus_sign:
    Kqg = -Kqg
    Kgq = -Kgq
    Kqq = np.eye(len(out["interpolation_xgrid"])) - ab * L * pqq0
    Kgg = np.eye(len(out["interpolation_xgrid"])) - ab * L * pgg0


# compute PDFs
if mode_g:
    f = np.array([pdf.xfxQ2(21, x, muf2) / x for x in out["interpolation_xgrid"]])
else:
    f = np.array([pdf.xfxQ2(4, x, muf2) / x for x in out["interpolation_xgrid"]])


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
            loq @ pqg1 + nlog @ (pgg0 - beta0I) + nloq @ pqg0,
        )
        ops["nnlosv2"] = (
            nnlosv2g,
            1.0 / 2.0 * loq @ pqq0 @ pqg0 + 1.0 / 2.0 * (loq @ pqg0 @ (pgg0 - beta0I)),
        )
    else:
        ops["nlosv"] = (nlosvc, loc @ pqq0)
        ops["nnlosv1"] = (
            nnlosv1c,
            loc @ pqq1 + nloc @ (pqq0 - beta0I) + nlog @ pgq0,
        )
        ops["nnlosv2"] = (
            nnlosv2c,
            1.0 / 2.0 * loq @ pqg0 @ pgq0 + 1.0 / 2.0 * (loc @ pqq0 @ (pqq0 - beta0I)),
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
        op = ab * (nlog + nlosvg * L)
    else:
        op = loc + ab * (nloc + nlosvc * L)
    print(cc1 / (op @ f))


check_c_res()
# check B EKO is K
print("check B EKO result")
ekob = legacy.load_tar("../data/ekos/2205/test.tar")
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
ekoc = legacy.load_tar("../data/ekos/3205/test.tar")
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
    plt.plot(bb1, label="b-fk")
    plt.plot(((loq + ab * nloq) @ (Kqg) + (ab * nlog) @ (Kgg)) @ f, label="ana_pred")
else:
    print(bb1 / (((loc + ab * nloc) @ Kqq + (ab * nlog) @ Kgq) @ f))
    plt.plot(bb1, label="b-fk")
    plt.plot(((loc + ab * nloc) @ Kqq + (ab * nlog) @ Kgq) @ f, label="ana_pred")
plt.legend()
plt.show()
# check difference between B and C
print("check B - C")
if order_mode == Order.nlo or order_mode == Order.nnlo:
    diff_grid = bb1 - cc1
    plt.plot(bb1, label="b-grid")
    plt.plot(cc1, label="c-grid")
    plt.legend()
    plt.show()
    if mode_g:
        # plt.plot(ab**2 * L * ((nloc @ pqg0 @ f)), label="pqg0")
        # plt.plot(ab**2 * L * ((nlog @ pgg0 @ f)), label="pgg0")
        diff_ana = (ab * ab * L * ((nloq @ pqg0) + (nlog @ pgg0))) @ f
    else:
        # plt.plot(a**2 * L * ((nloc @ pqq0 @ f)), label="pqq0")
        # plt.plot(a**2 * L * ((nlog @ pgq0 @ f)), label="pgq0")
        diff_ana = (ab * ab * L * ((nloc @ pqq0) + (nlog @ pgq0))) @ f
    print(diff_grid / cc1)
    print(bb1 / cc1)
    print(diff_grid / diff_ana)
    plt.plot(diff_grid, label="grid")
    plt.plot(diff_ana, label="ana")
    #     # plt.plot((diff_grid/bb1-1)*100, label="rel err. diff to b")
    #     # plt.plot(diff_grid/diff_ana, label="ratio")
    plt.legend()
    plt.show()

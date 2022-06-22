# -*- coding: utf-8 -*-
import eko
import lhapdf
import matplotlib.pyplot as plt
import numpy as np
from eko.anomalous_dimensions.as1 import gamma_ns
from eko.harmonics import S1
from ekomark import apply
from scipy.integrate import quad
from scipy.interpolate import interp1d


def mel(y, n):
    f = interp1d(o["targetgrid"], y)
    return quad(lambda x: x ** (n - 1.0) * f(x), min(o["targetgrid"]), 1.0)


o = eko.output.Output.load_tar("data/ekos/2201/noevol-withK-as0p35.tar")

resu = apply.apply_pdf(o, lhapdf.mkPDF("uonly"))
resd = apply.apply_pdf(o, lhapdf.mkPDF("donly"))
rest3 = apply.apply_pdf(o, lhapdf.mkPDF("T3only"))
restoyt3 = apply.apply_pdf(o, lhapdf.mkPDF("toyt3only"))
resS = apply.apply_pdf(o, lhapdf.mkPDF("Sonly"))
resNN40 = apply.apply_pdf(o, lhapdf.mkPDF("NNPDF40_nnlo_as_01180"))

u_u = [lhapdf.mkPDF("uonly").xfxQ2(2, x, 10) / x for x in o["targetgrid"]]
d_d = [lhapdf.mkPDF("donly").xfxQ2(1, x, 10) / x for x in o["targetgrid"]]
t3_u = [lhapdf.mkPDF("T3only").xfxQ2(2, x, 10) / x for x in o["targetgrid"]]
toyt3_u = [lhapdf.mkPDF("toyt3only").xfxQ2(2, x, 10) / x for x in o["targetgrid"]]
toyt3_d = [lhapdf.mkPDF("toyt3only").xfxQ2(1, x, 10) / x for x in o["targetgrid"]]
toyS_d = [lhapdf.mkPDF("Sonly").xfxQ2(1, x, 10) / x for x in o["targetgrid"]]
nn40_u = [
    lhapdf.mkPDF("NNPDF40_nnlo_as_01180").xfxQ2(2, x, 10) / x for x in o["targetgrid"]
]

g = np.array([gamma_ns(n, S1(n)) for n in range(1, 10)])

K = 1.0 - 0.35 / (4.0 * np.pi) * g * np.log(2**2)

melu_u = np.array([mel(u_u, n)[0] for n in range(1, 10)])
meld_d = np.array([mel(d_d, n)[0] for n in range(1, 10)])
melnn40_u = np.array([mel(nn40_u, n)[0] for n in range(1, 10)])

melresu_u = np.array([mel(resu[300.0]["pdfs"][2], n)[0] for n in range(1, 10)])
melresd_d = np.array([mel(resd[300.0]["pdfs"][1], n)[0] for n in range(1, 10)])
melresnn40_u = np.array([mel(resNN40[300.0]["pdfs"][2], n)[0] for n in range(1, 10)])

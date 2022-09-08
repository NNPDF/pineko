# -*- coding: utf-8 -*-
import yadism
import yaml
import numpy as np
from scipy.integrate import quad
from scipy.interpolate import interp1d
from eko.anomalous_dimensions import as1
from eko.harmonics import S1
from eko.interpolation import InterpolatorDispatcher

# def mel(y, n):
#     xs = out["interpolation_xgrid"]
#     f = interp1d(xs, y)
#     return quad(lambda x: x ** (n - 1.0) * f(x), min(xs), 1.0)

def mel2(out, ys, n):
    interp = InterpolatorDispatcher.from_dict(out)
    lnxmin = np.log(out["interpolation_xgrid"][0])
    res = 0.
    for y, bf in zip(ys, interp):
        pj = bf(n, lnxmin) * np.exp(n * lnxmin)
        res += y * pj
    return res


with open("210.yaml","r") as f: t = yaml.safe_load(f)
with open("test.yaml","r") as f: o = yaml.safe_load(f)
#out = yadism.output.Output.load_tar("test.tar")
out = yadism.run_yadism(t,o)
out.dump_tar("test.tar")

locbf10 = [out["F2_light"][j].orders[(0,0,0,0)][0][-3][10] for j in range(len(out["interpolation_xgrid"]))]
pqqcbf10 = [out["F2_light"][j].orders[(1,0,0,1)][0][-3][10] for j in range(len(out["interpolation_xgrid"]))]
pgqgbf10 = [out["F2_light"][j].orders[(1,0,0,1)][0][7][10] for j in range(len(out["interpolation_xgrid"]))]

mel2bf10 = np.array([mel2(out,[0]*10 + [1] + [0]*39,n) for n in range(1,10)])

mel2lobf10 = np.array([mel2(out,locbf10,n) for n in range(1,10)])
mel2pqqcbf10 = np.array([mel2(out,pqqcbf10,n) for n in range(1,10)])
mel2pgqgbf10 = np.array([mel2(out,pgqgbf10,n) for n in range(1,10)])

locbf20 = [out["F2_light"][j].orders[(0,0,0,0)][0][-3][20] for j in range(len(out["interpolation_xgrid"]))]
pqqcbf20 = [out["F2_light"][j].orders[(1,0,0,1)][0][-3][20] for j in range(len(out["interpolation_xgrid"]))]
pgqgbf20 = [out["F2_light"][j].orders[(1,0,0,1)][0][7][20] for j in range(len(out["interpolation_xgrid"]))]

mel2bf20 = np.array([mel2(out,[0]*20 + [1] + [0]*29,n) for n in range(1,10)])
mel2lobf20 = np.array([mel2(out,locbf20,n) for n in range(1,10)])
mel2pqqcbf20 = np.array([mel2(out,pqqcbf20,n) for n in range(1,10)])
mel2pgqgbf20 = np.array([mel2(out,pgqgbf20,n) for n in range(1,10)])

gns = np.array([as1.gamma_ns(n, S1(n)) for n in range(1, 10)])
ggq = np.array([np.nan if n == 1 else as1.gamma_gq(n) for n in range(1, 10)])

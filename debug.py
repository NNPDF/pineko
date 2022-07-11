# -*- coding: utf-8 -*-
import eko
import lhapdf
import numpy as np
from ekobox import apply

gonly = lhapdf.mkPDF("gonly", 0)

ho = eko.output.Output.load_tar("data/ekos/3201/test.tar")
hpdf = apply.apply_pdf(ho, gonly)

bo = eko.output.Output.load_tar("data/ekos/2201/test.tar")
bpdf = apply.apply_pdf(bo, gonly)

# a is the output of the sv script
plot(np.log(a[:, 2]), a[:, 4])
plot(np.log(a[:, 2]), a[:, 6])
plot(np.log(a[:, 2]), 4 * 5 / 9 * a[:, 2] * bpdf[300.0]["pdfs"][2])

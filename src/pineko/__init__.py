# -*- coding: utf-8 -*-
import pathlib
import shutil
import subprocess
import io
import re

import yaml
import numpy as np
import pandas as pd

import yadism
import eko
import pineappl


data = pathlib.Path(__file__).absolute().parents[2] / "data"
myoperator_path = data / "myoperator.yaml"
mydis_path = data / "mydis.pineappl"
myfktable_path = data / "myfktable.pineappl"

with open(data / "theory.yaml") as f:
    theory_card = yaml.safe_load(f)
with open(data / "operator.yaml") as f:
    operators_card = yaml.safe_load(f)
with open(data / "observable-simple.yaml") as f:
    observable_card = yaml.safe_load(f)


def generate_eko(target_filename, operators_card):
    ops = eko.run_dglap(theory_card=theory_card, operators_card=operators_card)
    ops.dump_yaml_to_file(target_filename)


def load_eko(operators_card):
    if not myoperator_path.exists():
        generate_eko(myoperator_path, operators_card)

    ev_ops = eko.output.Output.load_yaml_from_file(myoperator_path)
    return ev_ops


def generate_yadism(target_filename):
    dis_cf = yadism.run_yadism(theory=theory_card, observables=observable_card)
    dis_cf.dump_pineappl_to_file(str(target_filename), "F2total")


def load_pineappl():
    if not mydis_path.exists():
        generate_yadism(mydis_path)

    grid = pineappl.grid.Grid.read(str(mydis_path))
    return grid


def load_fake():
    class Grid:
        def eko_info(self):
            """eko_info.

            .. todo::
                docs
            """
            return dict(q2grid=[50], xgrid=[])

        def convolute_eko(self, operators, q0, pids):
            """convolute_eko.

            Parameters
            ----------
            operators :
                operators
            q0 :
                q0
            pids :
                pids

            .. todo::
                docs
            """
            return type(self)()

        def convolute(self, pdf):
            """convolute.

            Parameters
            ----------
            pdf :
                pdf

            .. todo::
                docs
            """
            return 0.0

        def write(self, target_filename):
            shutil.copy2(mydis_path, target_filename)

    return Grid()


# load pineappl
pineappl_grid = load_pineappl()
x_grid, q2_grid = pineappl_grid.eko_info()
operators_card["Q2grid"] = q2_grid
operators_card["interpolation_xgrid"] = x_grid

# load eko
operators = load_eko(operators_card)
operator_grid = np.array([list(operators["Q2grid"].values())[0]["operators"]])
pineappl_grid_q0 = pineappl_grid.convolute_eko(
    operators["q2_ref"], [0.1], operators["pids"], operator_grid
)
pineappl_grid_q0.write(str(myfktable_path))

import lhapdf

ct14llo = lhapdf.mkPDF("CT14llo_NF4")
# do the comparison
# prediction_high = pineappl_grid.convolute("CT14llo_NF4")
# prediction_low = pineappl_grid_q0.convolute("CT14llo_NF4")
comparison = subprocess.run(
    ["pineappl", "diff", str(mydis_path), str(myfktable_path), "CT14llo_NF4"],
    capture_output=True,
)

output = comparison.stdout.decode().splitlines()
stream = io.StringIO()
columns = "bin  x1      x1_2        x2  x2_2  pine1 pine2 diff".split()
for line in output:
    try:
        int(line.strip().split(" ")[0])
        isnum = True
    except ValueError:
        isnum = False

    if isnum:
        stream.write(line.strip() + "\n")
    elif line[:3] == "bin":
        pass
        line = re.sub(
            r"O\(.*\)",
            f"{mydis_path.stem}_prediction {myfktable_path.stem}_prediction diff",
            line.strip(),
        )
        columns = re.sub(r"(x\d*)", r"\1 \1_max", line).split()

stream.seek(0)
df = pd.read_table(stream, names=columns, sep=" ")

df.set_index("bin", inplace=True)
# remove bins' upper edges when bins are trivial
bin_not_relevant = True
if bin_not_relevant:
    obs_labels = np.unique([lab for lab in filter(lambda lab: "_" in lab, df.columns)])
    df.drop(obs_labels, axis=1, inplace=True)

print(df)
__import__("pdb").set_trace()

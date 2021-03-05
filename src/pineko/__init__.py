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
import eko, eko.strong_coupling
import pineappl


data = pathlib.Path(__file__).absolute().parents[2] / "data"
myoperator_path = data / "myoperator.yaml"
mydis_path = data / "mydis.pineappl"
mydis_yaml_path = data / "mydis.yaml"
mydy_path = data / "mydy.pineappl"
myfktable_path = data / "myfktable.pineappl"

with open(data / "theory.yaml") as f:
    theory_card = yaml.safe_load(f)
with open(data / "operator.yaml") as f:
    operators_card = yaml.safe_load(f)
with open(data / "observable.yaml") as f:
    observable_card = yaml.safe_load(f)


def generate_eko(target_filename, operators_card):
    ops = eko.run_dglap(theory_card=theory_card, operators_card=operators_card)
    ops.dump_yaml_to_file(target_filename)


def load_eko(operators_card):
    if not myoperator_path.exists():
        generate_eko(myoperator_path, operators_card)

    ev_ops = eko.output.Output.load_yaml_from_file(myoperator_path)
    return ev_ops


def eko_identity(shape):
    i, k = np.ogrid[: shape[1], : shape[2]]
    eko_identity = np.zeros(shape[1:], int)
    eko_identity[i, k, i, k] = 1
    return np.broadcast_to(eko_identity[np.newaxis, :, :, :, :], shape)


def generate_yadism(target_filename):
    dis_cf = yadism.run_yadism(theory=theory_card, observables=observable_card)
    dis_cf.dump_pineappl_to_file(str(target_filename), "F2total")
    dis_cf.dump_yaml_to_file(str(mydis_yaml_path))


def load_pineappl_dis():
    if not mydis_path.exists():
        generate_yadism(mydis_path)

    grid = pineappl.grid.Grid.read(str(mydis_path))
    return grid


def load_pineappl_dy():
    grid = pineappl.grid.Grid.read(str(mydy_path))
    return grid


dis = True
#  dis = False
# load pineappl
if dis:
    pineappl_grid = load_pineappl_dis()
    x_grid, q2_grid = pineappl_grid.eko_info()
else:
    pineappl_grid = load_pineappl_dy()
    x_grid, q2_grid = pineappl_grid.eko_info()
    q2_grid = [
        5442.305429193529,
        7434.731381687921,
        10243.85467001917,
        14238.990475802799,
    ]
operators_card["Q2grid"] = q2_grid
operators_card["interpolation_xgrid"] = x_grid

# load eko
print(q2_grid)
operators = load_eko(operators_card)

operator_grid = np.array([op["operators"] for op in operators["Q2grid"].values()])
alpha_s = (
    lambda q2: eko.strong_coupling.StrongCoupling.from_dict(theory_card).a_s(q2)
    * 4
    * np.pi
)

# for the time being replace with a fake one, for debugging
#  operator_grid = eko_identity(operator_grid.shape)

pineappl_grid_q0 = pineappl_grid.convolute_eko(alpha_s, operators)
pineappl_grid_q0.write(str(myfktable_path))

# do the comparison
# prediction_high = pineappl_grid.convolute("CT14llo_NF4")
# prediction_low = pineappl_grid_q0.convolute("CT14llo_NF4")
comparison = subprocess.run(
    [
        "pineappl",
        "diff",
        str(mydis_path if dis else mydy_path),
        str(myfktable_path),
        "CT14llo_NF4",
    ],
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
            #  f"{mydis_path.stem}_prediction {myfktable_path.stem}_prediction diff",
            f"{mydy_path.stem}_prediction {myfktable_path.stem}_prediction diff",
            line.strip(),
        )
        columns = re.sub(r"(x\d*)", r"\1 \1_max", line).split()

stream.seek(0)
df = pd.read_table(stream, names=columns, sep=" ")

df.set_index("bin", inplace=True)
# remove bins' upper edges when bins are trivial
bin_not_relevant = True
if bin_not_relevant:
    obs_labels = np.unique(
        [lab for lab in filter(lambda lab: "_" in lab and "my" not in lab, df.columns)]
    )
    df.drop(obs_labels, axis=1, inplace=True)

#  print(df)
pineappl_output = "\n".join(output)
print(pineappl_output)

__import__("pdb").set_trace()

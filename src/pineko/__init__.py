# -*- coding: utf-8 -*-
import pathlib

import numpy as np

import yaml
import eko
import pineappl

import yadism

here = pathlib.Path(__file__).absolute().parent

with open(here.parents[1] / "data" / "theory.yaml") as f:
    theory_card = yaml.safe_load(f)
with open(here.parents[1] / "data" / "operator.yaml") as f:
    operators_card = yaml.safe_load(f)
with open(here.parents[1] / "data" / "observable-simple.yaml") as f:
    observable_card = yaml.safe_load(f)


def generate_eko(target_filename, operators_card):
    ops = eko.run_dglap(theory_card=theory_card, operators_card=operators_card)
    ops.dump_yaml_to_file(target_filename)


def load_eko(operators_card):
    myoperator = here.parents[1] / "data" / "myoperator.yaml"
    if not myoperator.exists():
        generate_eko(myoperator, operators_card)

    ev_ops = eko.output.Output.load_yaml_from_file(myoperator)
    return ev_ops


def generate_yadism(target_filename):
    dis_cf = yadism.run_yadism(theory=theory_card, observables=observable_card)
    dis_cf.dump_pineappl_to_file(str(target_filename), "F2total")


def load_pineappl():
    mydis = here.parents[1] / "data" / "mydis.pineappl"
    if not mydis.exists():
        generate_yadism(mydis)

    grid = pineappl.grid.Grid.read(str(mydis))
    return grid


def load_fake():
    class Grid:
        def get_eko_infos(self):
            return dict(q2grid=[50], xgrid=[])

        def convolute(self, pdf):
            return 0.0

        def convolute_eko(self, operators):
            return type(self)()

        def write(self):
            pass

    return Grid()


# load pineappl
pineappl_grid = load_fake()
pineappl_info = pineappl_grid.get_eko_infos()
operators_card["Q2grid"] = pineappl_info["q2grid"]
operators_card["interpolation_xgrid"] = pineappl_info["xgrid"]

# load eko
operators = load_eko(operators_card)
pineappl_grid_q0 = pineappl_grid.convolute_eko(operators)
pineappl_grid_q0.write()

import lhapdf

ct14llo = lhapdf.mkPDF("CT14llo_NF6")
# do the comparison
prediction_high = pineappl_grid.convolute(ct14llo)
prediction_low = pineappl_grid_q0.convolute(ct14llo)

print(prediction_low, prediction_high)

__import__("ipdb").set_trace()

# def myekos(pids, zs, q2s):
# ekos = np.random.rand(len(q2s), len(pids), len(zs), len(pids), len(zs))
# return ekos


# x = 0.1
# pid = 1
# xin = 0.1
# pidin = 1
# q2 = 1.0e4
# pids = [1]
# zs = [0.1, 1.0]
# q2s = [q2]
# ekos = myekos(pids, zs, q2s)
# grid = load_pineappl()

# for pid_index, _ in enumerate(pids):
# for x_index, _ in enumerate(zs):
# grid.convolute_test(
# pid, x, q2, pids, zs, q2s, ekos[:, :, :, pid_index, x_index].tolist()
# )

# -*- coding: utf-8 -*-
import pathlib

import yaml
import eko
import pineappl

import yadism

here = pathlib.Path(__file__).absolute().parent

with open(here.parents[1] / "data" / "LO-EXA-FFNS.yaml") as f:
    theory_card = yaml.safe_load(f)


def generate_eko(target_filename):
    with open(here.parents[1] / "data" / "iter10-l30m20r4.yaml") as f:
        operators_card = yaml.safe_load(f)

    ops = eko.run_dglap(theory_card=theory_card, operators_card=operators_card)
    ops.dump_yaml_to_file(target_filename)


def load_eko():
    myoperator = here.parents[1] / "data" / "myoperator.yaml"
    if not myoperator.exists():
        generate_eko(myoperator)

    ev_ops = eko.output.Output.load_yaml_from_file(myoperator)
    return ev_ops


def generate_yadism(target_filename):
    with open(here.parents[1] / "data" / "observable-simple.yaml") as f:
        observable_card = yaml.safe_load(f)

    dis_cf = yadism.run_yadism(theory=theory_card, observables=observable_card)
    dis_cf.dump_pineappl_to_file(str(target_filename), "F2total")


def load_pineappl():
    mydis = here.parents[1] / "data" / "mydis.pineappl"
    if not mydis.exists():
        generate_yadism(mydis)

    grid = pineappl.grid.Grid.read(str(mydis))
    return grid


__import__("ipdb").set_trace()

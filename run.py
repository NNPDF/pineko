#!/usr/bin/env python

# -*- coding: utf-8 -*-
import pathlib

import eko
import pineappl
import yadism
import yaml

from pineko import convolute

data = pathlib.Path(__file__).absolute().parent / "data"
myoperator_base_path = data / "myoperator.yaml"
mydis_path = data / "mydis.pineappl"
mydis_yaml_path = data / "mydis.yaml"
mydy_path = data / "ATLASZHIGHMASS49FB.pineappl.lz4"
mydylo_path = data / "ATLASZHIGHMASS49FB-LO.pineappl.lz4"
myttbar_path = data / "CMSTTBARTOT5TEV.pineappl.lz4"
myttbarlo_path = data / "CMSTTBARTOT5TEV-LO.pineappl.lz4"
myfktable_base_path = data / "myfktable.pineappl"

with open(data / "theory.yaml") as f:
    theory_card = yaml.safe_load(f)


def ensure_eko(pineappl_path, target_filename):
    """Generate EKO on the fly"""
    if target_filename.exists():
        return
    with open(data / "operator.yaml") as f:
        operators_card = yaml.safe_load(f)

    pineappl_grid = pineappl.grid.Grid.read(str(pineappl_path))
    x_grid, q2_grid = pineappl_grid.eko_info()
    operators_card["Q2grid"] = q2_grid
    operators_card["interpolation_xgrid"] = x_grid
    ops = eko.run_dglap(theory_card=theory_card, operators_card=operators_card)
    ops.dump_yaml_to_file(target_filename)


def generate_yadism(target_filename):
    """Generate yadism on the fly"""
    t = theory_card.copy()
    t["PTO"] = 1
    with open(data / "observable.yaml") as f:
        observable_card = yaml.safe_load(f)
    dis_cf = yadism.run_yadism(theory=t, observables=observable_card)
    dis_cf.dump_pineappl_to_file(str(target_filename), "F2_total")
    dis_cf.dump_yaml_to_file(str(mydis_yaml_path))


# collect all path and fake the objects
pineappl_path = mydis_path
if "dis" in str(pineappl_path):
    generate_yadism(pineappl_path)
myoperator_path = myoperator_base_path.with_suffix(f".{pineappl_path.stem}.yaml")
ensure_eko(pineappl_path, myoperator_path)
myfktable_path = myfktable_base_path.with_suffix(
    "." + pineappl_path.stem + myfktable_base_path.suffix
)
# doit
convolute(pineappl_path, myoperator_path, myfktable_path, "CT14llo_NF4")

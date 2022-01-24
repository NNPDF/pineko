#!/usr/bin/env python

# -*- coding: utf-8 -*-
import pathlib

import eko
import pineappl
import yaml

from pineko import convolute

data = pathlib.Path(__file__).absolute().parent / "data"
myoperator_base_path = data / "myoperator.tar"
mydis_path = data / "mydis.pineappl.lz4"
mydis_yaml_path = data / "mydis.yaml"
mydy_path = data / "ATLASZHIGHMASS49FB.pineappl.lz4"
mydylo_path = data / "ATLASZHIGHMASS49FB-LO.pineappl.lz4"
myttbar_path = data / "ATLAS_TTB_8TEV_TOT.pineappl.lz4"
myttbarlo_path = data / "CMSTTBARTOT5TEV-LO.pineappl.lz4"
myfktable_base_path = data / "myfktable.pineappl.lz4"

with open(data / "theory_213.yaml") as f:
    theory_card = yaml.safe_load(f)


def ensure_eko(pineappl_path, target_filename):
    """Generate EKO on the fly"""
    if target_filename.exists():
        return
    with open(data / "operator.yaml") as f:
        operators_card = yaml.safe_load(f)

    pineappl_grid = pineappl.grid.Grid.read(str(pineappl_path))
    x_grid, _pids, muf2_grid = pineappl_grid.axes()
    operators_card["Q2grid"] = muf2_grid
    operators_card["targetgrid"] = x_grid
    ops = eko.run_dglap(theory_card=theory_card, operators_card=operators_card)
    ops.dump_tar(target_filename)


def generate_yadism(target_filename):
    """Generate yadism on the fly"""
    import yadism

    t = theory_card.copy()
    t["PTO"] = 0
    t["TMC"] = 0
    with open(data / "observable.yaml") as f:
        observable_card = yaml.safe_load(f)
    dis_cf = yadism.run_yadism(theory=t, observables=observable_card)
    dis_cf.dump_pineappl_to_file(str(target_filename), "F2_total")
    dis_cf.dump_yaml_to_file(str(mydis_yaml_path))


# collect all path and fake the objects
pineappl_path = mydis_path
if "dis" in str(pineappl_path):
    generate_yadism(pineappl_path)
pine_stem = str(pineappl_path.stem).rsplit(".", 1)[0]
myoperator_path = data / (myoperator_base_path.stem + "-" + pine_stem + ".tar")
ensure_eko(pineappl_path, myoperator_path)
fk_stem = str(myfktable_base_path.stem).rsplit(".", 1)[0]
myfktable_path = data / (fk_stem + "-" + pine_stem + ".pineappl.lz4")
# doit
convolute(pineappl_path, myoperator_path, myfktable_path, "NNPDF40_lo_as_01180")

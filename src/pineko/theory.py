# -*- coding: utf-8 -*-
import logging

import eko
import rich
import yaml

from . import configs, parser, theory_card

class TheoryBuilder:
    """Common builder application to create the ingredients for a theory.

    Parameters
    ----------
    theory_id : int
        theory identifier
    datsets : list(str)
        list of datasets
    """
    def __init__(self, theory_id, datasets):
        self.theory_id = theory_id
        self.datasets = datasets

    @property
    def eko_path(self):
        """Suffix path with theory id"""
        return configs.configs["paths"]["ekos"] / str(self.theory_id)

    def ekos(self, logs):
        """Compute all ekos.

        Parameters
        ----------
        logs : bool
            save eko logs?
        """
        # setup data
        paths = configs.configs["paths"]
        tcard = theory_card.load(self.theory_id)
        self.eko_path.mkdir(exist_ok=True)
        # iterate datasets
        for ds in self.datasets:
            rich.print(f"Analyze {ds}")
            # iterate grids
            grids = parser.load_grids(self.theory_id, ds)
            for name in grids.keys():
                opcard_path = paths["operator_cards"] / f"{name}.yaml"
                with open(opcard_path, encoding="utf-8") as f:
                    ocard = yaml.safe_load(f)
                eko_filename = self.eko_path / f"{name}.tar"
                # activate logging
                if logs and paths["logs"]["eko"]:
                    log_path = paths["logs"]["eko"] / f"{self.theory_id}-{name}.log"
                    logStdout = logging.FileHandler(log_path)
                    logStdout.setLevel(logging.INFO)
                    logStdout.setFormatter(logging.Formatter("%(message)s"))
                    logging.getLogger("eko").handlers = []
                    logging.getLogger("eko").addHandler(logStdout)
                    logging.getLogger("eko").setLevel(logging.INFO)
                # do it!
                ops = eko.run_dglap(theory_card=tcard, operators_card=ocard)
                ops.dump_tar(eko_filename)
                if eko_filename.exists():
                    rich.print(f"[green]Success:[/] Wrote EKO to {eko_filename}")
            rich.print()

# -*- coding: utf-8 -*-
import logging

import eko
import rich
import yaml

from . import configs, evolve, parser, theory_card


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

    @property
    def fk_path(self):
        """Suffix path with theory id"""
        return configs.configs["paths"]["fktables"] / str(self.theory_id)

    def iterate(self, f, **kwargs):
        """Iterated grids in datasets.

        Additional keyword arguments are simply passed down.

        Parameters
        ----------
        f : callable
            iterated callable recieving name and grid as argument
        """
        for ds in self.datasets:
            rich.print(f"Analyze {ds}")
            grids = parser.load_grids(self.theory_id, ds)
            for name, grid in grids.items():
                f(name, grid, **kwargs)
            rich.print()

    def opcard(self, name, grid):
        """Write a single operator card.

        Parameters
        ----------
        name : str
            grid name, i.e. it's true stem
        grid : pathlib.Path
            path to grid
        """
        paths = configs.configs["paths"]
        opcard_path = paths["operator_cards"] / f"{name}.yaml"
        _x_grid, q2_grid = evolve.write_operator_card_from_file(
            grid, paths["opcard_template"], opcard_path
        )
        if opcard_path.exists():
            rich.print(
                f"[green]Success:[/] Wrote card with {len(q2_grid)} Q2 points to {opcard_path}"
            )

    def opcards(self):
        """Write operator cards."""
        self.iterate(self.opcard)

    def eko(self, name, _grid, tcard, logs):
        """Compute a single eko.

        Parameters
        ----------
        name : str
            grid name, i.e. it's true stem
        grid : pathlib.Path
            path to grid
        tcard : dict
            theory card
        logs : bool
            save eko logs?
        """
        # setup data
        paths = configs.configs["paths"]
        opcard_path = paths["operator_cards"] / f"{name}.yaml"
        with open(opcard_path, encoding="utf-8") as f:
            ocard = yaml.safe_load(f)
        eko_filename = self.eko_path / f"{name}.tar"
        # activate logging
        if logs and paths["logs"]["eko"]:
            log_path = paths["logs"]["eko"] / f"{self.theory_id}-{name}.log"
            logFile = logging.FileHandler(log_path)
            logFile.setLevel(logging.INFO)
            logFile.setFormatter(logging.Formatter("%(message)s"))
            logging.getLogger("eko").handlers = []
            logging.getLogger("eko").addHandler(logFile)
            logging.getLogger("eko").setLevel(logging.INFO)
        # do it!
        ops = eko.run_dglap(theory_card=tcard, operators_card=ocard)
        ops.dump_tar(eko_filename)
        if eko_filename.exists():
            rich.print(f"[green]Success:[/] Wrote EKO to {eko_filename}")

    def ekos(self, logs):
        """Compute all ekos.

        Parameters
        ----------
        logs : bool
            save eko logs?
        """
        tcard = theory_card.load(self.theory_id)
        self.eko_path.mkdir(exist_ok=True)
        self.iterate(self.eko, tcard=tcard, logs=logs)

    def fk(self, name, grid_path, tcard, pdf, logs):
        """Compute a single FK table.

        Parameters
        ----------
        name : str
            grid name, i.e. it's true stem
        grid_path : pathlib.Path
            path to grid
        tcard : dict
            theory card
        pdf : str
            comparison PDF
        logs : bool
            save eko logs?
        """
        # setup data
        paths = configs.configs["paths"]
        eko_filename = self.eko_path / f"{name}.tar"
        fk_filename = self.fk_path / f"{name}.{parser.ext}"
        max_as = 1 + int(tcard["PTO"])
        max_al = 0
        # do it!
        _grid, _fk, comparison = evolve.evolve_grid(
            grid_path, eko_filename, fk_filename, max_as, max_al, pdf
        )
        # activate logging
        if logs and paths["logs"]["fk"] and comparison:
            logfile = paths["logs"]["fk"] / f"{self.theory_id}-{name}-{pdf}.log"
            logfile.write_text(comparison.to_string())
        if fk_filename.exists():
            rich.print(f"[green]Success:[/] Wrote FK table to {fk_filename}")

    def fks(self, pdf, logs):
        """Compute all FK tables.

        Parameters
        ----------
        pdf : str
            comparison PDF
        logs : bool
            save eko logs?
        """
        tcard = theory_card.load(self.theory_id)
        self.fk_path.mkdir(exist_ok=True)
        self.iterate(self.fk, tcard=tcard, pdf=pdf, logs=logs)

"""Shared utilities for pineko.

Common tools typically used by several pineko functions.
"""

from .configs import GENERIC_OPTIONS, THEORY_PATH_KEY


def _nnpdf_enabled(configs):
    """Check whether NNPDF is enabled."""
    if configs is None:
        return True
    return configs.get(GENERIC_OPTIONS, {}).get("nnpdf", False)


def read_grids_from_nnpdf(dataset_name, configs=None):
    """Read the list of fktables given a dataset name.

    If NNPDF is not available, returns None.

    Parameters
    ----------
        dataset_name: str
        configs: dict
            dictionary of configuration options
            if None it it assumed that the NNPDF version is required
    """
    if not _nnpdf_enabled(configs):
        return None

    # Import NNPDF only if we really want it!
    from nnpdf_data import legacy_to_new_map
    from validphys.commondataparser import EXT
    from validphys.loader import Loader

    # We only need the metadata, so this should be enough
    dataset_name, variant = legacy_to_new_map(dataset_name)
    cd = Loader().check_commondata(dataset_name, variant=variant)
    fks = cd.metadata.theory.FK_tables
    # Return it flat
    return [f"{i}.{EXT}" for operand in fks for i in operand]


def load_nnpdf_theory(theory_id, configs):
    """Load a theory using the NNPDF data utilities.

    If NNPDF is not available, returns None.

    Parameters
    ----------
        theory_id: int
        configs: dict
            dictionary of configuration options
    """
    if not _nnpdf_enabled(configs):
        return None

    from nnpdf_data.theorydbutils import fetch_theory

    theory_path = configs["paths"][THEORY_PATH_KEY]
    return fetch_theory(theory_path, theory_id)

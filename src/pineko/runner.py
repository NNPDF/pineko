import eko
import pineappl
import rich
import rich.box
import rich.panel

from .comparator import compare


def from_files(pineappl_path, eko_path, fktable_path, comparison_pdf=None):
    """
    Invoke steps from file paths.

    Parameters
    ----------
        pineappl_path : str
            unconvoluted grid
        eko_path : str
            evolution operator
        fktable_path : str
            target path for convoluted grid
        comparison_pdf : None or str
            if given, a comparison table (with / without evolution) will be printed
    """
    rich.print(
        rich.panel.Panel.fit(f"Computing ...", style="magenta", box=rich.box.SQUARE),
        f"  {pineappl_path}",
        f"\n+ {eko_path}",
        f"\n= {fktable_path}",
    )
    # load
    pineappl_grid = pineappl.grid.Grid.read(str(pineappl_path))
    operators = eko.output.Output.load_yaml_from_file(eko_path)
    # doit
    fktable = pineappl_grid.convolute_eko(operators)
    # write
    fktable.write(str(fktable_path))
    # compare before after
    if comparison_pdf is not None:
        print(compare(pineappl_path, fktable_path, comparison_pdf))

import pathlib

from pineko.evolve import write_operator_card_from_file

data = pathlib.Path(__file__).absolute().parent / "data"
data2 = pathlib.Path(__file__).absolute().parent / "data2"

write_operator_card_from_file(data / "mydis.pineappl.lz4", data / "operator.yaml", data2 / "test.yaml")

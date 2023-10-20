import numpy as np
import pytest
import yaml

import pineko

# @pytest.mark.parametrize("theoryid,is_mixed", [(400, False), (208, True)])
# def benchmark_produce_fonll_tcards(
#     tmp_path, test_files, test_configs, theoryid, is_mixed
# ):
#     tcard = pineko.theory_card.load(theoryid)
#     tcard_paths_list = pineko.fonll.produce_fonll_tcards(tcard, tmp_path, theoryid)
#     # Check they are correct
#     theorycards = []
#     for path in tcard_paths_list:
#         with open(path, encoding="UTF-8") as f:
#             theorycards.append(yaml.safe_load(f))
#     for num_fonll_tcard, fns, nfff, po, part in zip(
#         theorycards,
#         np.array(pineko.fonll.MIXED_FNS_CONFIG).transpose().tolist()[0]
#         if is_mixed
#         else np.array(pineko.fonll.FNS_CONFIG).transpose().tolist()[0],
#         np.array(pineko.fonll.MIXED_FNS_CONFIG).transpose().tolist()[1]
#         if is_mixed
#         else np.array(pineko.fonll.FNS_CONFIG).transpose().tolist()[1],
#         pineko.fonll.produce_ptos(tcard["FNS"], is_mixed),
#         np.array(pineko.fonll.MIXED_FNS_CONFIG).transpose().tolist()[2]
#         if is_mixed
#         else np.array(pineko.fonll.FNS_CONFIG).transpose().tolist()[2],
#     ):
#         assert num_fonll_tcard["FNS"] == fns
#         assert num_fonll_tcard["NfFF"] == int(nfff)
#         assert (
#             num_fonll_tcard["PTO"] == po - 1 if is_mixed and fns == "FONLL-FFN0" else po
#         )
#         assert num_fonll_tcard["FONLLParts"] == part

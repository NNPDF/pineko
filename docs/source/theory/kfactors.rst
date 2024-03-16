K-Factors
=========

Another useful tool that `pineko` includes is ``pineko kfactor`` which allows the embedding of a kfactor
as a proper order in a grid. The usage is the following::

  pineko kfactor GRIDS_FOLDER KFACTOR_FOLDER YAMLDB_FILE TARGET_FOLDER PTO_TO_UPDATE --order_exists

where ``GRIDS_FOLDER`` is the folder containing the grids to update, ``KFACTOR_FOLDER`` is the folder
containing the kfactor files and ``YAMLDB_FILE`` is the path to the yamldb file of the requested dataset.
The other inputs have already been described in the previous section.
``PTO_TO_UPDATE`` is the :math:`\alpha_s` perturbative order to update or create, with the convention that 
``LO=1``, ``NLO=2`` and so on, irrespectively to the powers of alpha_s.
Note that only pure QCD kfactors are taken into account.
If the flag ``order_exists`` is passed the kfactor is applied to the specified perturbative order.

For example to add the NNLO in a grid containing at most NLO one has to select ``PTO_TO_UPDATE=2``;
nn the other hand to reweight the NNLO present in a grid with a kfactor, 
one should do ``PTO_TO_UPDATE=2 --order_exists``.
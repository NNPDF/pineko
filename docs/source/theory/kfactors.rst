K-Factors
=========

Another useful tool that `pineko` includes is ``pineko kfactor`` which allows the embedding of a kfactor
as a proper order in a grid. The usage is the following::

  pineko kfactor GRIDS_FOLDER KFACTOR_FOLDER YAMLDB_PATH TARGET_FOLDER MAX_AS ORDER_EXISTS

where ``GRIDS_FOLDER`` is the folder containing the grids to update, ``KFACTOR_FOLDER`` is the folder
containing the kfactor files and ``YAMLDB_PATH`` is the path to the yamldb file of the requested dataset.
The other inputs have already been described in the previous section.

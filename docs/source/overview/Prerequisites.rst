#############
Prerequisites
#############

Generating a *theory*, as defined above, requires several files which are
described next.

*pineko.toml*
-------------

You need to provide a *pineko.toml*, that provides all necessary paths to the input and output folders.
[**DEBUG**: Look at the **DEBUG** example in this repo [1]_.]

*ymldb*
-------

You need all files of the *ymldb* [2]_.  [**DEBUG**: Look at the respective *load.sh* script to load from dom.]
This defines the mapping from datasets to FK tables.

Theory Runcards
---------------

You need to provide the necessary theory runcards named with their respective theory ID inside the *paths.theory_cards* folder [3]_.

Default Operator Card
---------------------

You need to provide a default operator card for |EKO| [4]_.
[**DEBUG**: Look at the respective *load.sh* script to load from dom.]

Grids
-----

*pineko* does **NOT** compute grids, which are instead expected input to *pineko*.
There are typically two ways to obtain grids: computing them from scratch with `runcards <https://github.com/NNPDF/runcards/>`_
or reusing existing ones.

Generate new Grids with *rr*
""""""""""""""""""""""""""""

You need to run *rr* with a given theory runcard and put the generated grid file with the same name
inside the *paths.grids/theory_id* folder. The name has to match the *ymldb* which is the case by default.

Inherit Grids from Existing Theory
""""""""""""""""""""""""""""""""""

You can reuse the grids from a different theory by running:: 

  pineko theory inherit-grids SOURCE_THEORY_ID TARGET_THEORY_ID DATASET1 DATASET2 ...

The relation between the source theory and the target theory is non-trivial [5]_.


Notes
-----

.. [1] Actually, instead we should provide a concise description here - but let's wait to be stable first

.. [2] this is to be replaced by the new CommonData format

.. [3] this is to be replaced by a binding to the true theory DB

.. [4] I'm thinking how to improve this, because how could we provide a study on the interpolation accuracy? at the moment there just equal

.. [5] examples being SV, different evolution settings, etc.



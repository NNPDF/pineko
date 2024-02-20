################
Running `pineko`
################

Running *pineko* consists of two steps - each of them being potentially computationally expensive:
computing the |EKO| and convoluting the |EKO| with the grid.

Computing the |EKO|
-------------------

Generating new |EKO|
""""""""""""""""""""

This is a two step process:

#. Generate the necessary operator cards with::

    pineko theory opcards THEORY_ID DATASET1 DATASET2 ...

   Note that it is also possible to generate the operator card for a single grid doing::

    pineko opcard GRID DEFAULT_CARD opcard

   eventually setting ``--xif`` to the wanted value.

#. Generate the actual EKOs with::

    pineko theory ekos THEORY_ID DATASET1 DATASET2 ...



Inherit |EKO| or grids from Existing Theory
"""""""""""""""""""""""""""""""""""""""""""

You can reuse the |EKO| from a different theory by running::

  pineko theory inherit-ekos SOURCE_THEORY_ID TARGET_THEORY_ID DATASET1 DATASET2 ...

You can reuse the grid from a different theory by running::

  pineko theory inherit-grids SOURCE_THEORY_ID TARGET_THEORY_ID DATASET1 DATASET2 ...

The relation between the source theory and the target theory is non-trivial [5]_.

Generating the FK Table
-----------------------

You need to have the |EKO| computed in the previous step.
Then you can convolute the |EKO| with the grids by running::

  pineko theory fks THEORY_ID DATASET1 DATASET2 ...

Note that you can also convolute a single grid with a single eko (obtaining a single FK table) by running::

  pineko convolute GRID OPCARD FKTABLE MAX_AS MAX_AL

If necessary it is possible to specify the values of the *renormalization* and *factorization* scale variations with
the options ``--xir`` and ``--xif``.


Generating FONLL FK Tables
--------------------------

In order to generate FK tables with (numerical) |FONLL| the different flavor schemes
need to be evolved separately and joined together in a single FK table only
in the final step.

There are 2 workflows possible, one in which all the steps are performed individually
and one that is more automatized.

The automatize workflows always assumes that |FONLL| is performed both for
charm and bottom effects.

The manual procedure works as follow:

  1. Generate 7 theories for all the different flavor patches with command::

      pineko fonll_tcards THEORY_ID

    The different flavor patches are named following the convention:

      * ``THEORY_ID00`` : |FFNS| :math:`n_f=3`
      * ``THEORY_ID01`` : |FFN0| :math:`n_f=3`
      * ``THEORY_ID02`` : massless component of |FFNS| :math:`n_f=4`
      * ``THEORY_ID03`` : massive component of |FFNS| :math:`n_f=4`
      * ``THEORY_ID05`` : massless component of |FFNS| :math:`n_f=5`
      * ``THEORY_ID06`` : massive component of |FFNS| :math:`n_f=5`

    where for |FFNS| :math:`n_f=4,5` massive and massless parts are splitted to
    allow for a damping option.

  2. Generate the grids corrisponding to all the 7 theories with the external program.

  3. Generate the operator cards for each theory with the usual command.
     Note that, in principle, only 3 ekos are needed, as there are only 3 different :math:`n_f` patches.
     So you might speed up the procedure taking advantage of inherit-ekos.

  4. Generate the ekos for each theory with the usual commands.

  5. Generate the FK tables each of the 7 theories with the usual commands.

  6. Combine the various FK tables into a single file, using the command::

      pineko combine_fonll THEORY_ID DATASET --FFNS3 THEORY_ID00 --FFN03 THEORY_ID01 --FFNS4til THEORY_ID02 --FFNS4bar THEORY_ID03 --FFN04 THEORY_ID04 --FFNS5til THEORY_ID05 --FFNS5bar THEORY_ID06

    where the first 3 theories are needed to perform |FONLL| on charm effects,
    while the last 4 are needed to include also bottom effects.

The automatize procedure can be faster, but it might be less flexible.
In this case the workflows is:

  1. Generate 7 theories for all the different flavor patches with the command::

      pineko fonll_tcards THEORY_ID

    See above for the intermediate theories naming convention.

  2. Generate the grids corrisponding to all the 7 theories with the external program.

  3. Generate the ekos for only 3 theories and inherit the others running::

      pineko fonll_ekos THEORY_ID DATASET1 DATASET2 ...

    Note: this is usually an expensive operation as multiple ekos are run sequentially.
    Depending on the resources that you have available it might be more convinient
    to call the command separately for each DATASET.

  4. Generate the final |FONLL| FK table directly running::

      pineko fonll_fks THEORY_ID DATASET1 DATASET2 ...


Other functionalities
---------------------

Other than the fundamental functions that have been described so far, *pineko* has a few
handy utility functions.

Checking the grids
""""""""""""""""""

Under the subcommand ``pineko check`` you can find two possible useful checks:

1.  **compatibility**. This is used to check if a *grid* and an *eko* are compatible and ready to generate an Fk table. In order for a grid and an eko to be compatible, they must have the same x and Q2 grid (eventually including the factorization scale variations). The check is used as
  ::

    pineko check compatibility GRID EKO

  eventually specifying the value of the factorization scale variation with the option ``--xif``.
2.  **scvar**. This is used to check if the provided grid contains the requested scale variations. The syntax is the following
  ::

    pineko check scvar GRID SCALE AS_ORDER AL_ORDER

  where ``SCALE`` can be one between "ren" and "fact" (respectively for *renormalization* and
  *factorization* scale variations).

Comparing grids and FK tables
"""""""""""""""""""""""""""""

With the command ``pineko compare`` it is possible to compare the predictions as provided by the grid
(convoluted with a |PDF|) with the predictions as provided by the FK table. This is done like::

  pineko compare GRID FKTABLE MAX_AS MAX_AL PDF

again eventually specifying the values of *renormalization* and *factorization* scales with the
appropriate options.

Scale variations
""""""""""""""""

Since it is possible to compute scale variations terms at a certain perturbative order N+1 just from
the knowledge of the central N order (see https://pineko.readthedocs.io/en/latest/theory/scalevar.html),
`pineko` includes a tool to add the required scale variations order to a grid which contain the
necessary central orders. The command to run it is::

  pineko ren_sv_grid GRID_PATH OUTPUT_FOLDER_PATH MAX_AS NF ORDER_EXISTS

where ``GRID_PATH`` is the path of the original grid, ``OUTPUT_FOLDER_PATH`` is the folder where the
updated grid will be dumped, ``MAX_AS`` is the requested perturbative order of the QCD coupling and
``NF`` is the number of active flavors one wants to consider when computing the scale variations terms.
If the original grid has already all the scale variations terms for the requested perturbative order,
`pineko` will do nothing. If one want to force `pineko` to overwrite the already existing orders, it is
enough to set ``ORDER_EXISTS`` to `True`.

KFactors
""""""""

Another useful tool that `pineko` includes is ``pineko kfactor`` which allows the embedding of a kfactor
as a proper order in a grid. The usage is the following::

  pineko kfactor GRIDS_FOLDER KFACTOR_FOLDER YAMLDB_PATH TARGET_FOLDER MAX_AS ORDER_EXISTS

where ``GRIDS_FOLDER`` is the folder containing the grids to update, ``KFACTOR_FOLDER`` is the folder
containing the kfactor files and ``YAMLDB_PATH`` is the path to the yamldb file of the requested dataset.
The other inputs have already been described in the previous section.

Notes
-----

.. [5] examples being scale variations, different DIS settings, etc.

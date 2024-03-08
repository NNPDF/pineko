FONLL
=====

In order to generate |FK| tables with |FONLL| the different flavor schemes
need to be evolved separately and joined together in a single |FK| table only
in the final step.

There are 2 workflows possible, one in which all the steps are performed individually
and one that is more automatized.

The automatized workflows always assumes that |FONLL| is performed both for
charm and bottom effects.

Manual procedure
----------------

  1. Generate 7 theories for all the different flavor patches with command::

      pineko fonll tcards THEORY_ID

    The different flavor patches are named following the convention:

      * ``<THEORY_ID>00`` : |FFNS| :math:`n_f=3`
      * ``<THEORY_ID>01`` : |FFN0| :math:`n_f=3`
      * ``<THEORY_ID>02`` : massless component of |FFNS| :math:`n_f=4`
      * ``<THEORY_ID>03`` : massive component of |FFNS| :math:`n_f=4`
      * ``<THEORY_ID>04`` : |FFN0| :math:`n_f=4`
      * ``<THEORY_ID>05`` : massless component of |FFNS| :math:`n_f=5`
      * ``<THEORY_ID>06`` : massive component of |FFNS| :math:`n_f=5`

    where for |FFNS| :math:`n_f=4,5` massive and massless parts are split to
    allow for a damping option.

  2. Generate the grids corresponding to all the 7 theories with the external program.

  3. Generate the operator cards for each theory with the normal command listed above.
     Note that, in principle, only 3 ekos are needed, as there are only 3 different :math:`n_f` patches.
     So you might speed up the procedure taking advantage of inherit-ekos.

  4. Generate the ekos for each theory with the normal command listed above.

  5. Generate the |FK| tables each of the 7 theories with the normal command listed above.

  6. Combine the various |FK| tables into a single file, using the command::

      pineko fonll combine THEORY_ID DATASET --FFNS3 THEORY_ID00 --FFN03 THEORY_ID01 --FFNS4zeromass THEORY_ID02 --FFNS4massive THEORY_ID03 --FFN04 THEORY_ID04 --FFNS5zeromass THEORY_ID05 --FFNS5massive THEORY_ID06

    where the first 3 theories are needed to perform |FONLL| on charm effects,
    while the last 4 are needed to include also bottom effects.

Automatic procedure
-------------------

This workflow can be faster, but it might be less flexible:

  1. Generate 7 theories for all the different flavor patches with the command::

      pineko fonll tcards THEORY_ID

    See above for the intermediate theories naming convention.

  2. Generate the grids corresponding to all the 7 theories with the external program.

  3. Generate the three ekos, one for each :math:`n_f`, and inherit the others running::

      pineko fonll ekos THEORY_ID DATASET1 DATASET2 ...

    Note: this is usually an expensive operation as multiple ekos are run sequentially.
    Depending on the resources that you have available it might be more convenient
    to call the command separately for each DATASET.

  4. Generate the final |FONLL| |FK| table directly running::

      pineko fonll fks THEORY_ID DATASET1 DATASET2 ...

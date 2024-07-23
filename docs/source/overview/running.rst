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

The relation between the source theory and the target theory is non-trivial
(e.g. they may differ by scale variations, different DIS settings, etc).

Generating the FK Table
-----------------------

You need to have the |EKO| computed in the previous step.
Then you can convolve the |EKO| with the grids by running::

  pineko theory fks THEORY_ID DATASET1 DATASET2 ...

Note that you can also convolve a single grid with a single eko (obtaining a single FK table) by running::

  pineko convolve GRID FKTABLE MAX_AS MAX_AL OP_PATH_1 OP_PATH_2

If necessary it is possible to specify the values of the *renormalization* and *factorization* scale variations with
the options ``--xir`` and ``--xif``.

Other functionalities
---------------------

Other than the fundamental functions that have been described so far, *pineko* has a few
handy utility functions:

- applying the :doc:`FONLL prescription</theory/fonll>`
- applying the :doc:`scale variation prescription</theory/scalevar>`
- burning the :doc:`K-factor</theory/kfactors>` into grids


Checking the grids
""""""""""""""""""

Under the subcommand ``pineko check`` you can find two possible useful checks:

1.  **compatibility**. This is used to check if a *grid* and an *eko* are compatible and ready to generate an |FK| table.
    In order for a grid and an eko to be compatible, they must have the same x and Q2 grid (eventually including the
    factorization scale variations). The check is used as

      pineko check compatibility GRID EKO

    eventually specifying the value of the factorization scale variation with the option ``--xif``.
2.  **scvar**. This is used to check if the provided grid contains the requested scale variations. The syntax is the following

      pineko check scvar GRID SCALE AS_ORDER AL_ORDER

    where ``SCALE`` can be one between "ren" and "fact" (respectively for *renormalization* and
    *factorization* scale variations).

Comparing grids and FK tables
"""""""""""""""""""""""""""""

With the command ``pineko compare`` it is possible to compare the predictions as provided by the grid
(convolved with a |PDF|) with the predictions as provided by the |FK| table. This is done like

  pineko compare GRID FKTABLE MAX_AS MAX_AL PDF_1 PDF_2

again eventually specifying the values of *renormalization* and *factorization* scales with the
appropriate options.

Using pineko with NNPDF
"""""""""""""""""""""""

It is possible to use ``pineko`` without providing an explicit mapping between data and grids
(i.e., without a ``yamldb`` database) or theory cards, by using the data declared in the NNPDF
repository (which includes a data-theory mapping).

In order to do this you need to install ``pineko`` with the ``nnpdf`` extra, which installs
the latest version from the ``nnpdf`` repository::

  pip install pineko[nnpdf]

In order to enable ``pineko`` to read the data from ``nnpdf`` it is necessary to set up
the ``general::nnpdf`` key in the configuration file.
Note that if you do that, both ``theory_cards`` and ``ymldb`` keys become unnecessary,
like in the example below.


.. code-block:: yaml

  [general]
  nnpdf = true

  [paths]
  grids = "data/grids"
  operator_card_template_name = "../_template.yaml"
  operator_cards = "data/operator_cards"
  ekos = "data/ekos"
  fktables = "data/fktables"

  [paths.logs]
  eko = "logs/eko"
  fk = "logs/fk"

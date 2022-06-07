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


#. Generate the actual EKOs with::

    pineko theory ekos THEORY_ID DATASET1 DATASET2 ...



Inherit |EKO| from Existing Theory
"""""""""""""""""""""""""""""""""""

You can reuse the |EKO|"s from a different theory by running::

  pineko theory inherit-ekos SOURCE_THEORY_ID TARGET_THEORY_ID DATASET1 DATASET2 ...


The relation between the source theory and the target theory is non-trivial [6]_.

Generating the FK Table
-----------------------

You need to have the |EKO| computed in the previous step.
Then you can convolute the |EKO| with the grids by running::

  pineko theory fks THEORY_ID DATASET1 DATASET2 ...


Notes
-----

.. [6] examples being SV, different DIS settings, etc.

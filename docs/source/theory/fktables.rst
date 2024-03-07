
Fast Kernel (FK) tables
=======================

The direct calculation of observables during a |PDF| fit is not very practical
since it requires first solving the |DGLAP| evolution equation for each new boundary
condition at the initial scale :math:`Q_0` and then convoluting with the coefficient
functions of the partonic cross-sections.

For this reason, we adopt the |FK| tables method :cite:`Ball:2010` which is presented in this section.

In the framework of collinear |QCD| factorization cross section, such as the :math:`F_2` |DIS| structure function,
can be decomposed in terms of hard-scattering coefficient functions and PDFs as,

.. math::

    F_2(x,Q^2) &=  \mathbf{C}(Q^2) \otimes \mathbf{f}(Q^2) \\
    &= \mathbf{C}(Q^2) \otimes \mathbf{E}(Q^2 \leftarrow Q_0^2) \otimes \mathbf{f}(Q_0^2),


where :math:`\mathbf{C}(Q^2)` are the process-dependent coefficient functions which
can be computed perturbatively as an expansion in the |QCD| and |QED|
couplings,  :math:`\mathbf{E}(Q^2 \leftarrow Q_0^2)` is an evolution operator, determined by the
solutions of the |DGLAP| equations, which evolves the |PDF| from the initial
parameterization scale :math:`Q_0^2` up to the hard-scattering scale :math:`Q^2`,
:math:`\mathbf{f}(Q^2_0)` are the |PDF| at the parameterization scale, and
:math:`\otimes` denotes the Mellin convolution.

In the above equation (and in all equations from now on), the sum over flavors (running over
the contributing quarks and anti-quarks, as well as over the gluon) is indicated by the bold font.

.. In the same way, a hadronic cross-section :math:`\sigma` can be written as,

.. .. math::

..     \sigma(Q^2) &= \mathbf{\hat{\sigma}}(Q^2) \otimes_{1} \mathbf{f}_1(Q^2) \otimes_2 \mathbf{f}_2(Q^2) \\
..     &= \hat{\sigma}(x_{1},x_{2},Q^2) \otimes \mathbf{\mathcal{L}}(x_{1},x_{2},Q^2) \\
..     &= \hat{\sigma}(x_{1},x_{2},Q^2) \otimes \mathbf{\text{E}(Q^2 \leftarrow Q_0^2) \otimes \mathcal{L}(x_{1}.x_{2},Q_0^2),

.. where :math:`\hat{\sigma}(x_{1},x_{2},Q^2)` are the process-dependent partonic cross-sections and
.. :math:`\mathcal{L} = f \otimes f` is called luminosity.

To evaluate the observable in a computationally more efficient way, it is better
to precompute all the perturbative information:
for the partonic coefficient functions :math:`\mathbf{C}` we use |pineappl| grids and
for the evolution operators :math:`\mathbf{E}` we use |eko|.

Finally, we can arrive at

.. math::

    \begin{align}
    F_2(x,Q^2) &= \sum_{\alpha} \mathbf{FK}(x,x_{\alpha},Q^2\leftarrow Q^2_0) \cdot \mathbf{f}(x_{\alpha},Q_0^2)
    \end{align}

where all of the information about the partonic cross-sections and the |DGLAP|
evolution operators is now encoded into the so-called |FK| table :math:`\mathbf{FK}`.

.. Doing the same for the hadronic cross-sections lead to

.. .. math::

..     \sigma(Q^2) = \sum_{\alpha}^{n_x} \text{FK}_{\alpha \beta}(x_{\alpha}, x_{\beta},Q^2,Q^2_0) \, \mathcal{L}(x_{\alpha}, x_{\beta},Q_0^2).

.. _fktables:

============================================================
Fast Kernel (FK) tables
============================================================


.. raw:: latex

   \tableofcontents

Here we discuss the numerical implementation of the calculations of both the DIS structure functions
and the hadronic cross-sections.

The direct calculation of such observables during the PDF fit is not practical
since it requires first solving the DGLAP evolution equation for each new boundary
condition at the initial scale :math:`Q_0` and then convoluting with the coefficient
functions or the partonic cross-sections. 

For this reason, we adopt the FK tables method which is presented in this section.

In the framework of collinear QCD factorization, the :math:`F_2` structure function
can be decomposed in terms of hard-scattering coefficient functions and PDFs as,

.. math::

    F_2(x,Q^2) &=  C(Q^2) \otimes f(Q^2) \nonumber \\
    &= C(Q^2) \otimes \text{E}(Q^2 \leftarrow Q_0^2) \otimes f(Q_0^2),
    

where :math:`C(Q^2)` are the process-dependent coefficient functions which
can be computed perturbatively as an expansion in the |QCD| and |QED|
couplings;  :math:`\text{E}(Q^2 \leftarrow Q_0^2)` is an evolution operator, determined by the
solutions of the DGLAP equations, which evolves the PDF from the initial
parameterization scale :math:`Q_0^2` into the hard-scattering scale :math:`Q^2`,
:math:`f(Q^2_0)` are the PDFs at the parameterization scale, and
:math:`\otimes` denotes the Mellin convolution.

In the above equation (and in all the equations from now on), the sum over flavors running over the :math:`n_f` 
active quarks and antiquarks flavors at a given scale :math:`Q`, as well as over the gluon, is left implicit.

In the same way, the hadronic cross-section :math:`\sigma` can be written as,

.. math::
 
    \sigma(Q^2) &= \hat{\sigma}(x_{1},x_{2},Q^2) \otimes f(x_{1},Q^2) \otimes f(x_{2},Q^2) \nonumber \\
    &= \hat{\sigma}(x_{1},x_{2},Q^2) \otimes \mathcal{L}(x_{1},x_{2},Q^2) \nonumber \\
    &= \hat{\sigma}(x_{1},x_{2},Q^2) \otimes \text{E}(Q^2 \leftarrow Q_0^2) \otimes \mathcal{L}(x_{1}.x_{2},Q_0^2),

where :math:`\hat{\sigma}(x_{1},x_{2},Q^2)` are the process-dependent partonic cross-sections and
:math:`\mathcal{L} = f \otimes f` is called luminosity.

To evaluate the observable in a more computationally efficient way, it is better 
to precompute all the perturbative information, i.e. the coefficient functions :math:`C`,
or the partonic cross-sections :math:`\hat{\sigma}`,
and the evolution operators :math:`\text{E}`, with a suitable
interpolation basis.

Several of these approaches have been made available in the context of
PDF fits.
The DIS structure functions are provided by |yadism| while the grids for the hadronic 
cross-sections are provided by |pineappl|. 

Within this approach, we can factorize the dependence on the PDFs at the input scale :math:`Q_0` as follows.

First, we introduce an expansion over a set of interpolating functions :math:`\{ p_{\beta}\}` spanning :math:`x` such that

.. math::

    
    f(x,Q^2) = \sum_{\beta} f_{\beta \tau} p_{\beta}(x) \, ,
    

where the PDFs are now tabulated
in a grid in the :math:`(x,Q^2)` plane, :math:`f_{\beta \tau}\equiv f(x_\beta,Q^2_{\tau})`.

We can express this result in terms of the PDFs at the input evolution scale
using the (interpolated) DGLAP evolution operators,

.. math::

    f_{\beta \tau} = \sum_{\alpha} \text{E}^{\tau}_{\alpha \beta}\,f(x_{\alpha},Q_0^2) \, ,    

so that the nuclear DIS structure function can be evaluated as

.. math::

    F_2(x,Q^2) = C(x,Q^2) \otimes \left[
    \sum_{\alpha,\beta} \text{E}^{\tau}_{\alpha \beta}\,f(x_{\alpha},Q_0^2) p_{\beta}(x) \right]\, .

This can be rearranged to give

.. math::

    \begin{align}
    F_2(x,Q^2) &= \sum_{\alpha}^{n_x} \text{FK}_{\alpha}(x,x_{\alpha},Q^2,Q^2_0) \, f(x_{\alpha},Q_0^2) 
    \end{align}

where all of the information about the partonic cross-sections and the DGLAP
evolution operators is now encoded into the so-called FK table, :math:`\text{FK}_{\alpha}`.

Doing the same for the hadronic cross-sections lead to 

.. math::

    \sigma(Q^2) = \sum_{\alpha}^{n_x} \text{FK}_{\alpha \beta}(x_{\alpha}, x_{\beta},Q^2,Q^2_0) \, \mathcal{L}(x_{\alpha}, x_{\beta},Q_0^2). 

For a more detailed explanation please have a look to |EKO| documentation.

Therefore, with the **pineko** method we are able to
express the series of convolutions by a matrix
multiplication, increasing the numerical 
calculation speed by up to several orders
of magnitude.

For a more detailed report on the **FKtables** maethod please see :cite:`Ball:2010`


.. _fktables:

============================================================
Fast Interface (FK tables)
============================================================

.. raw:: latex

   \maketitle

.. raw:: latex

   \tableofcontents

Here we discuss the numerical implementation of the calculations of both the DIS structure functions
and the hadronic cross-sections.

In the framework of collinear QCD factorization, the :math:`F_2` structure function
can be decomposed in terms of hard-scattering coefficient functions and PDFs as,

.. math::

    \begin{align} 
    \label{eq:ev} 
    F_2(x,Q^2) &= \sum_i^{n_f} C_i(x,Q^2) \otimes f_i(x,Q^2) \nonumber \\
    &= \sum_{i,j}^{n_f} C_i(x,Q^2) \otimes \text{E}_{ij}(Q^2,Q_0^2) \otimes f_j(x,Q_0^2),
    \end{align}

where :math:`C_i(x,Q^2)` are the process-dependent coefficient functions which
can be computed perturbatively as an expansion in the QCD and QED
couplings;  :math:`\text{E}_{ij}(Q^2,Q_0^2)` is an evolution operator, determined by the
solutions of the DGLAP equations, which evolves the PDF from the initial
parameterization scale :math:`Q_0^2` into the hard-scattering scale :math:`Q^2`,
:math:`f_i(x,Q^2_0)` are the PDFs at the parameterization scale, and
:math:`\otimes` denotes the Mellin convolution.

The sum over flavors :math:`i,j` runs over the :math:`n_f` active quarks and antiquarks flavors at a given
scale :math:`Q`, as well as over the gluon.

In the same way, the hadronic cross-section :math:`\sigma` can be written as,

.. math::

    \begin{align} 
    \label{eq:ev_had} 
    \sigma(Q^2) &= \sum_{i,j}^{n_f} \hat{\sigma}_{ij}(x_{1},x_{2},Q^2) \otimes f_i(x_{1},Q^2) \otimes f_j(x_{2},Q^2) \nonumber \\
    &= \sum_{i,j}^{n_f} \hat{\sigma}_{ij}(x_{1},x_{2},Q^2) \otimes \mathcal{L}_{ij}(x_{1},x_{2},Q^2) \nonumber \\
    &= \sum_{i,j,k,l}^{n_f} \hat{\sigma}_{ij}(x_{1},x_{2},Q^2) \otimes \text{E}_{ijkl}(Q^2,Q_0^2) \otimes \mathcal{L}_{kl}(x_{1}.x_{2},Q_0^2),
    \end{align}

where :math:`\hat{\sigma}_{ij}(x_{1},x_{2},Q^2)` are the process-dependent partonic cross-sections and
:math:`\mathcal{L}_{ij} = f_i \otimes f_j` is called luminosity.

The direct calculation of the above equations during the PDF fit is not practical
since it requires first solving the DGLAP evolution equation for each new boundary
condition at :math:`Q_0` and then convoluting with the coefficient
functions or the partonic cross-sections.

To evaluate the observable in a more computationally efficient way, it is better 
to precompute all the perturbative information, i.e. the coefficient functions :math:`C_i`,
or the partonic cross-sections :math:`\hat{\sigma}_{ij}`,
and the evolution operators :math:`\text{E}`, with a suitable
interpolation basis.

Several of these approaches have been made available in the context of
PDF fits.
Here we use |pineappl| to precompute the perturbative
information, which are provided by |yadism| for DIS structure functions and by |pineappl| itself for hadronic 
cross-sections.

Within this approach, we can factorize the dependence on the PDFs at the input scale :math:`Q_0` as follows.

First, we introduce an expansion over a set of interpolating functions :math:`\{ I_{\beta}\}` spanning :math:`x` such that

.. math::

    \begin{equation}
    f_i(x,Q^2) = \sum_{\beta} f_{i,\beta \tau} I_{\beta}(x) \, ,
    \end{equation}

where the PDFs are now tabulated
in a grid in the :math:`(x,Q^2)` plane, :math:`f_{i,\beta \tau}\equiv f_i(x_\beta,Q^2_{\tau})`.

We can express this result in terms of the PDFs at the input evolution scale
using the (interpolated) DGLAP evolution operators,

.. math::

    \begin{equation}
    f_{i,\beta \tau} = \sum_j \sum_{\alpha} \text{E}^{\tau}_{ij,\alpha \beta}\,f_j(x_{\alpha},Q_0^2) \, ,
    \end{equation}

so that the nuclear DIS structure function can be evaluated as

.. math::

    \begin{equation}
    F_2(x,Q^2) = \sum_i^{n_f} C_i(x,Q^2) \otimes \left[
    \sum_{\alpha,\beta} \sum_j \text{E}^{\tau}_{ij,\alpha \beta}\,f_j(x_{\alpha},Q_0^2) I_{\beta}(x) \right]\, .
    \end{equation}

This can be rearranged to give

.. math::

    \begin{align}
    \label{eq:ev_interp}
    F_2(x,Q^2) &= \sum_i^{n_f} \sum_{\alpha}^{n_x} \text{FK}_{i,\alpha}(x,x_{\alpha},Q^2,Q^2_0) \, f_i(x_{\alpha},Q_0^2) 
    \end{align}

where all of the information about the partonic cross-sections and the DGLAP
evolution operators is now encoded into the so-called FK table, :math:`\text{FK}_{i,\alpha}`.

Doing the same for the hadronic cross-sections lead to 

.. math::

    \begin{align}
    \label{eq:ev_interp}
    \sigma(Q^2) &= \sum_i^{n_f} \sum_{\alpha}^{n_x} \text{FK}_{i\alpha j \beta}(x_{\alpha}, x_{\beta},Q^2,Q^2_0) \, \mathcal{L}_{ij}(x_{\alpha}, x_{\beta},Q_0^2). 
    \end{align}

Therefore, with the **pineko** method we are able to
express the series of convolutions by a matrix
multiplication, increasing the numerical 
calculation speed by up to several orders
of magnitude.


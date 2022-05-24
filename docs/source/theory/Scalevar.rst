****************************
|MHOU| from scale variations
****************************
The variation of the **renormalization** and **factorization** scales is one of the most used method to estimate |MHOU| in |QCD|. 

This is due to the semplicity of both their calculation and their implementation, the former given by the fact that the scale dependence
of the strong coupling :math:`\alpha_{s}` and of |PDF| is universal and the latter given by the easiness in calculating the correlations.

However, the scale variations approach also has well known drawbacks:

* there is no unique principle to determine the specific range of the scale variation
* it cannot deal with new singularities or color structrures appearing at higher orders.

Here we briefly summarize the aspects of the scale variations method which are related to **pineko**. For a much more exhaustive 
report on how to compute scale variations and how to use them in a |PDF| fit, please refer to :cite:`NNPDF:ThUncerta`.

Renormalization group invariance
################################

Considering a theoretical prediction :math:`\overline{T}(\alpha_{s}(\mu^2), \mu^2/Q^2)` with :math:`\mu^2` the *renormalization* scale and 
:math:`Q^2` the typical scale of the process, denote with :math:`T(Q^2)` the same theoretical prediction evaluated at :math:`\mu^2 = Q^2`.

We know that the |QCD| running coupling satisfies the |RGE|

.. math::

    \mu^2 \frac{d}{d\mu^2}\alpha_{s}(\mu^2) = \beta(\alpha_{s}(\mu^2)) 

and that an all-order prediction is independent of the renormalization scale:

.. math::

    \mu^2 \frac{d}{d\mu^2}\overline{T}(\alpha_{s}(\mu^2), \mu^2/Q^2) = 0.

Then, defining :math:`\mu^2 = k Q^2`, :math:`t = \ln{(Q^2/\Lambda^2)}` and :math:`\kappa = \ln{k} = \ln{(\mu^2/Q^2)}`, we can rewrite
the RG equation as 

.. math::

    \frac{\delta}{\delta t}\overline{T}(\alpha_{s}(t+\kappa),\kappa)\bigg|_{\kappa} + \frac{\delta}{\delta \kappa}\overline{T}(\alpha_{s}(t+\kappa),\kappa)\bigg|_{\alpha_{s}}

which plugged in the Taylor expansion of :math:`\overline{T}(\alpha_{s},\kappa)`

.. math::

    \overline{T}(\alpha_{s}(t+\kappa),\kappa) = \overline{T}(\alpha_{s}(t+\kappa),0) - \kappa \frac{\delta}{\delta t}\overline{T}(\alpha_{s}(t+\kappa),0)\bigg|_{\kappa} + \dots

allow us to determine the scale-dependent terms at any given order just from the central predictions as

.. math::

    \overline{T}_{\text{LO}}(\alpha_{s}(t+\kappa),\kappa) &= T_{\text{LO}}(t + \kappa), \\
    \overline{T}_{\text{NLO}}(\alpha_{s}(t+\kappa),\kappa) &= T_{\text{NLO}}(t+\kappa) - \kappa \frac{d}{dt}T_{\text{LO}}(t + \kappa),  \\
    \overline{T}_{\text{NNLO}}(\alpha_{s}(t+\kappa),\kappa) &= T_{\text{NNLO}}(t+\kappa) - \kappa \frac{d}{dt}T_{\text{NLO}}(t + \kappa) + \frac{1}{2} \kappa^2 \frac{d^2}{dt^2}T_{\text{LO}}(t + \kappa).

From the last equation is then clearly possible to estimate the |MHOU| at any given order as :math:`\Delta(t,k) = \overline{T}(\alpha_{s}(t+\kappa),\kappa) - T(t)`. However,
as previously mentioned, there is no unique principle to determine the range of the scale variations, i.e. the value of :math:`\kappa`. Usually, one varies the renormalization 
scale by a factor of two, which means :math:`\kappa \in [-\ln{4}, \ln{4}]`.

Since we are usually interested in processes with one or more hadrons in the initial state, for which the cross-section is factorized into a partonic part and a |PDF| 
(or luminosity), we must deal with two sources of independent |MHOU|: 

* The uncertainties coming from the expansion of the partonic cross-sections
* The uncertainties coming from the expansion of the anomalous dimensions which determine the perturbative evolution of the |PDF|.

In the next section we will consider both the cases and we will provide the final equations for both *electroproduction* (i.e. with one incoming hadron) 
and *hadronic processes* (i.e. with two incoming hadron). In the anomalous dimensions case, we will also provide three different procedure (*schemes*) to estimate them. 

Scale variation for partonic cross-sections
###########################################

Electroproduction
=================

Consider the case of electroproduction, such as |DIS|, with the scale-dependent structure function given by

.. math::

    \overline{F}(t,\kappa) = \overline{C}(\alpha_{s}(t+\kappa),\kappa) \otimes f(t).

Since we are not varying the scale at which the |PDF| is evaluated, the RG invariace of the structure function implies the RG invariance
of the coefficients function :math:`\overline{C}(\alpha_{s}(t+\kappa),\kappa)`. Exploiting this property, is then possible to obtain:

.. math::

    \overline{C}(\alpha_{s}(t+\kappa),\kappa) = c_{0} + \alpha_{s}(t+\kappa)c_{1} + \alpha_{s}^{2}(t+\kappa)(c2 - \kappa \beta_{0} c_{1}) + \dots 

where :math:`\beta_{0}` is the first term of the perturbative expansion of the beta function and :math:`c_{i}` are the coefficients of 
the perturbative expansion of the scale-independent coefficients function, i.e.

.. math::

    C(t) = c_{0} + \alpha_{s}(t)c_{1} + \alpha_{s}^{2}(t)c_{2} + \dots

Note that convoluting the scale-varied coefficients function with the |PDF| lead to an expression which has the same structure of the 
scale-independent expression. This means evaluating the scale-varied structure function is very straightforward since all that is 
necessary is to change the coefficients in the perturbative expansion at the central scale.


Hadronic processes
==================

Let's now consider an hadronic process with scale-varied cross-section given by

.. math::

    \overline{\Sigma}(t,\kappa) = \overline{H}(\alpha_{s}(t+\kappa), \kappa) \otimes (f(t) \otimes f(t) ).

With the same procedure adopted in the electroproduction case, we can get 

.. math::

    \overline{H}(\alpha_{s}(t+\kappa),\kappa) = \alpha_{s}^{n}h_{0} + \alpha_{s}^{n+1}(h1 - \kappa n \beta{0} h_{0}) + \dots 

where this time the perturbative expansion of :math:`\overline{H}(\alpha_{s}(t+\kappa),\kappa)` starts at :math:`\mathcal{O}(\alpha_{s}^{n})` rather 
than :math:`\mathcal{O}(\alpha_{s}^{0})`.

Scale variation for |PDF| evolution
###########################################

A completely independent source of |MHOU| arises from the truncation of the perturbative expansion of the anomalous dimensions governing the evolution
of the |PDF|. Again, this uncertainties can be estimated trough scale variation but, in this case, there are three equivalent ways in which it can be
performed: at the level of anomalous dimensions, at |PDF| level or even at the level of the partonic cross-sections. We will address these different 
methods as *schemes*. 

Consider a |PDF| evaluated at the scale :math:`\mu`, :math:`f(\mu^2)`.

Schemes
=======



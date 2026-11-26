QED couplings
=============

With |QED| corrections switched on (``QED > 0`` in the theory card), the electromagnetic coupling
enters an |FK| table in two places, and the two use different definitions of the coupling.

Hard cross sections
-------------------

The hard-scattering grids are computed by external codes (MG5_aMC, NNLOJET, yadism, run through
``pinefarm``) in the :math:`G_\mu` scheme.
There the electroweak coupling is derived from the Fermi constant and the gauge-boson masses,

.. math::

    \alpha_{G_\mu} = \frac{\sqrt{2}}{\pi} G_F M_W^2 \left(1 - \frac{M_W^2}{M_Z^2}\right)
    \simeq \frac{1}{132.1} \, ,

and it does not run (it is a fixed coupling).

A |pineappl| grid stores the powers of :math:`\alpha` of each of its orders, not the
value of the coupling, so *pineko* never uses :math:`\alpha_{G_\mu}` itself.

PDF evolution
-------------

The |QED| DGLAP evolution of the |PDF| in the |EKO| depends on the running coupling
:math:`\alpha_{\rm em}(\mu^2)`.

This running coupling is the solution of the |QED| renormalization group equation in
the |MSbar| scheme, with the quark and lepton thresholds.

*pineko* passes the theory-card value
``alphaqed`` to |eko| as the boundary condition :math:`\alpha_{\rm em}(Q_{\rm ref})`, and sets the
reference scale of the |QED| coupling equal to ``Qref``, so that |eko| runs :math:`\alpha_{\rm em}`
together with :math:`\alpha_s`.

For this reason ``alphaqed`` must be the running |MSbar| coupling, e.g.
:math:`\hat{\alpha}^{(5)}(M_Z)^{-1} = 127.930 \pm 0.008` :cite:`PDG:2024`. It must not be the fixed
:math:`\alpha_{G_\mu}` of the hard cross sections, which is about 3% smaller and does not obey the
|QED| renormalization group equation.

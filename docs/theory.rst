Theory and Background
====================

This section provides the theoretical foundation for gravity modeling and explains the mathematical principles implemented in the software.

Gravitational Attraction
------------------------

The gravitational field at any point is determined by the density distribution of surrounding masses. For a continuous density distribution ρ(x,y,z), the gravitational potential Φ is given by:

.. math::

   \Phi(x,y,z) = G \iiint \frac{\rho(x',y',z')}{\sqrt{(x-x')^2 + (y-y')^2 + (z-z')^2}} \, dx' \, dy' \, dz'

where G is the gravitational constant (6.67430 × 10⁻¹¹ m³ kg⁻¹ s⁻²).

The gravitational acceleration components are the gradients of the potential:

.. math::

   g_x = -\frac{\partial\Phi}{\partial x}, \quad g_y = -\frac{\partial\Phi}{\partial y}, \quad g_z = -\frac{\partial\Phi}{\partial z}

Gravity Anomalies
-----------------

In geophysical applications, we typically work with gravity anomalies - the difference between observed gravity and a reference field (usually the normal gravity field of the Earth).

**Bouguer Anomaly**: Corrects for elevation and terrain effects:

.. math::

   \Delta g_B = g_{obs} - g_{normal} + 0.3086h - 0.0419\rho h

where:
- :math:`g_{obs}` is observed gravity
- :math:`g_{normal}` is normal gravity
- h is elevation
- ρ is crustal density

Forward Modeling
----------------

Forward modeling calculates the gravitational field for a known density distribution. The software implements several methods:

Discrete Element Method
~~~~~~~~~~~~~~~~~~~~~~~

For discretized models, the gravity field is computed as:

.. math::

   \Delta g(x,y,z) = G \sum_{i=1}^N \frac{\rho_i V_i (z - z_i)}{r_i^3}

where:
- :math:`\rho_i` is density of element i
- :math:`V_i` is volume of element i
- :math:`r_i` is distance from observation point to element center

This approximation is valid when the distance to the element is much larger than the element size.

Fast Fourier Transform (FFT) Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For large 2D grids, FFT methods provide efficient computation:

.. math::

   \Delta g(k_x, k_y) = G \rho h \cdot 2\pi G e^{-|k|d} \cdot \tilde{\rho}(k_x, k_y)

where :math:`\tilde{\rho}` is the 2D Fourier transform of the density distribution.

Inverse Problem
---------------

The inverse problem involves estimating subsurface density from gravity measurements. This is an ill-posed problem requiring regularization.

Tikhonov Regularization
~~~~~~~~~~~~~~~~~~~~~~~

The standard approach minimizes:

.. math::

   \min_\rho \left( \| g_{obs} - g_{calc}(\rho) \|^2 + \lambda \| L\rho \|^2 \right)

where:
- :math:`g_{obs}` are observed gravity values
- :math:`g_{calc}(\rho)` is calculated gravity for density ρ
- L is a regularization operator (often a Laplacian)
- λ is the regularization parameter

Iterative Methods
~~~~~~~~~~~~~~~~~

The software implements iterative solvers:

1. **Conjugate Gradient**: Efficient for large systems
2. **Gauss-Newton**: For nonlinear problems
3. **Levenberg-Marquardt**: Hybrid approach combining gradient and Newton methods

Resolution and Uncertainty
--------------------------

Model Resolution
~~~~~~~~~~~~~~~~

The resolving power depends on:

- **Survey geometry**: Station spacing and coverage
- **Measurement precision**: Gravity meter accuracy
- **Depth**: Deeper structures have lower resolution
- **Density contrast**: Larger contrasts are easier to resolve

Resolution matrix R relates true and estimated parameters:

.. math::

   \hat{\rho} = R \rho_{true}

The spread of R indicates resolution quality.

Uncertainty Analysis
~~~~~~~~~~~~~~~~~~~

Parameter uncertainties are estimated using the posterior covariance:

.. math::

   C_p = (G^T C_d^{-1} G + C_p^{-1})^{-1}

where:
- G is the sensitivity matrix
- :math:`C_d` is data covariance
- :math:`C_p` is prior parameter covariance

Practical Considerations
------------------------

Coordinate Systems
~~~~~~~~~~~~~~~~~~

The software uses Cartesian coordinates with:
- X: Easting (positive east)
- Y: Northing (positive north)
- Z: Elevation (positive up)

Units
~~~~~

- **Density**: g/cm³ or kg/m³
- **Gravity**: mGal (10⁻⁵ m/s²) or μGal (10⁻⁸ m/s²)
- **Distance**: meters
- **Mass**: kg

The pint library ensures consistent unit handling throughout calculations.

Numerical Stability
~~~~~~~~~~~~~~~~~~~

Several techniques ensure numerical stability:

1. **Adaptive quadrature**: For near-field calculations
2. **FFT filtering**: Removes high-frequency noise
3. **Preconditioning**: Improves convergence of iterative solvers
4. **Regularization**: Prevents overfitting

Applications
------------

Mineral Exploration
~~~~~~~~~~~~~~~~~~~

- Ore body delineation
- Kimberlite pipe detection
- Massive sulfide identification

Oil and Gas
~~~~~~~~~~~

- Salt dome imaging
- Basement structure mapping
- Reservoir characterization

Engineering Geology
~~~~~~~~~~~~~~~~~~~

- Cavity detection
- Foundation studies
- Groundwater basin mapping

Academic Research
~~~~~~~~~~~~~~~~~

- Lithospheric studies
- Isostatic compensation analysis
- Planetary geophysics

Limitations
-----------

1. **Non-uniqueness**: Multiple density distributions can produce similar gravity fields
2. **Depth ambiguity**: Deeper structures have broader anomalies
3. **Density uncertainty**: Requires independent density estimates
4. **Terrain effects**: Complex topography requires careful correction
5. **Noise sensitivity**: Requires high-quality gravity data

Best Practices
--------------

1. **Survey Design**: Plan surveys with appropriate station spacing
2. **Quality Control**: Apply drift corrections and tidal reductions
3. **Terrain Correction**: Use high-resolution DEMs for accurate corrections
4. **Independent Constraints**: Incorporate borehole or seismic data
5. **Validation**: Compare results with known geology
6. **Uncertainty Quantification**: Always estimate parameter uncertainties

For more detailed mathematical treatment, see classical texts like "Potential Theory in Gravity and Magnetic Applications" by Blakely (1996) or "Gravity and Magnetic Exploration" by Hinze et al. (2013).
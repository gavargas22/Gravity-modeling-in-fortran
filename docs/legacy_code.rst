Legacy Code
===========

This section documents the original Fortran codebase that has been modernized into Python.

Original Fortran Files
----------------------

The following Fortran files were part of the original gravity modeling implementation:

- ``main.f`` - Main program entry point
- ``mod1.f`` - Model initialization and setup
- ``inver.f`` - Inversion algorithms
- ``plot.f`` - Plotting routines
- ``svd.f`` - Singular value decomposition utilities
- ``talw.f`` - TALW algorithm implementation
- ``rotate.f`` - Coordinate rotation functions

Key Algorithms
--------------

TALW Algorithm
~~~~~~~~~~~~~~

The TALW (Talwani) algorithm is used for forward modeling of gravity anomalies from 3D density distributions. The algorithm integrates the gravitational attraction of rectangular prisms.

.. math::

   g(x,y,z) = G \int \int \int \frac{\rho(x',y',z')}{(r)^2} dx' dy' dz'

where:
- :math:`G` is the gravitational constant
- :math:`\rho` is the density distribution
- :math:`r` is the distance from the observation point to the source point

Inversion Methods
~~~~~~~~~~~~~~~~~

The original code implemented several inversion techniques:

1. **Tikhonov Regularization** - Adds a penalty term to stabilize the solution
2. **Total Variation Regularization** - Preserves sharp edges in the model
3. **Smoothness Regularization** - Encourages smooth solutions

Data Formats
------------

Input data was typically provided in text files with the following format:

- Column 1: X coordinate
- Column 2: Y coordinate
- Column 3: Z coordinate (elevation)
- Column 4: Observed gravity anomaly
- Column 5: Measurement uncertainty

Migration to Python
-------------------

The Fortran codebase has been modernized to Python with the following improvements:

- Object-oriented design with ``GMModel`` class
- Enhanced validation and error handling
- Progress reporting and callbacks
- Serialization support (JSON format)
- Integration with modern Python scientific libraries (NumPy, SciPy, Matplotlib)
- GUI interface using PySide6
- Comprehensive documentation with Sphinx

The core algorithms remain mathematically equivalent to the original Fortran implementation, ensuring consistency of results.
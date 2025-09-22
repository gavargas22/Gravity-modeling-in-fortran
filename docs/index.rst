.. Gravity Modeling documentation master file, created by
   sphinx-quickstart on Sun Sep 21 20:58:57 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Gravity Modeling documentation
==============================

Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Gravity Modeling
================

A modern Python implementation of gravity modeling algorithms, originally ported from legacy Fortran code. This package provides tools for geophysical gravity modeling, inversion, and visualization with both a graphical user interface and programmatic API.

.. image:: https://img.shields.io/badge/Python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :alt: License

Overview
--------

Gravity modeling is a geophysical technique used to understand subsurface density variations by analyzing gravitational field anomalies. This package implements various gravity modeling algorithms including:

- **Forward Modeling**: Calculate gravitational effects of subsurface structures
- **Inversion**: Estimate subsurface density distributions from gravity measurements
- **Visualization**: 2D and 3D plotting of gravity fields and subsurface models
- **Batch Processing**: Automated processing of multiple datasets

Key Features
~~~~~~~~~~~~

- **Modern Python API**: Clean, object-oriented interface
- **Graphical User Interface**: PySide6-based GUI for interactive modeling
- **Multiple Data Formats**: Support for legacy Fortran formats and modern JSON
- **Advanced Visualization**: Matplotlib-based 2D/3D plotting
- **Scientific Units**: Pint integration for proper unit handling
- **Cross-platform**: Windows, macOS, and Linux support
- **Batch Processing**: Automated workflows for large datasets

Quick Start
-----------

Installation
~~~~~~~~~~~~

Install from source::

    git clone https://github.com/your-repo/gravity-modeling.git
    cd gravity-modeling
    uv install

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    from gmm import GravityModel

    # Load a project
    model = GravityModel.from_json('examples/ore_body_2d/project.json')

    # Calculate gravity field
    gravity = model.calculate_gravity()

    # Visualize results
    model.plot_2d_field()

GUI Application
~~~~~~~~~~~~~~~

Launch the graphical interface::

    python -m src.gravity_modeling_app

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   gui_guide
   api_reference
   examples
   theory

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide

   contributing
   testing
   legacy_code

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


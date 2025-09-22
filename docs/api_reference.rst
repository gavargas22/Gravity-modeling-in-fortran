API Reference
=============

This section provides detailed documentation for all public classes, methods, and functions in the Gravity Modeling package.

Core Module (gmm.gm)
--------------------

.. automodule:: gmm.gm
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

GMModel Class
~~~~~~~~~~~~~

The main class for gravity/magnetics modeling operations.

.. autoclass:: gmm.gm.GMModel
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Inversion Module (gmm.inversion)
---------------------------------

.. automodule:: gmm.inversion
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Inversion Function
~~~~~~~~~~~~~~~~~~

.. autofunction:: gmm.inversion.execute_inversion

Complete Inversion Module (gmm.inversion_complete)
---------------------------------------------------

.. automodule:: gmm.inversion_complete
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

API Module (gmm.api)
--------------------

.. automodule:: gmm.api
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Types Module (gmm.types)
------------------------

.. automodule:: gmm.types
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

TALW Module (gmm.talw)
----------------------

.. automodule:: gmm.talw
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

GUI Application (gravity_modeling_app)
---------------------------------------

.. automodule:: gravity_modeling_app
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

GravityModelingApp Class
~~~~~~~~~~~~~~~~~~~~~~~~

The main GUI application class.

.. autoclass:: gravity_modeling_app.GravityModelingApp
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

MatplotlibCanvas Class
~~~~~~~~~~~~~~~~~~~~~~~

Canvas for displaying matplotlib plots in the GUI.

.. autoclass:: gravity_modeling_app.MatplotlibCanvas
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

InversionWorker Class
~~~~~~~~~~~~~~~~~~~~~

Worker thread for running inversion operations.

.. autoclass:: gravity_modeling_app.InversionWorker
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

BatchProcessingWorker Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Worker thread for batch processing multiple projects.

.. autoclass:: gravity_modeling_app.BatchProcessingWorker
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:
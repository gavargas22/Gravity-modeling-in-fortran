GUI User Guide
==============

The Gravity Modeling GUI provides an intuitive interface for interactive geophysical modeling. This guide covers all major features and workflows.

Getting Started
---------------

Launching the GUI
~~~~~~~~~~~~~~~~~

Start the graphical interface from the command line::

    python -m src.gravity_modeling_app

Or if installed as a package::

    gravity-modeling-gui

The main window will appear with the following components:

- **Menu Bar**: File operations, tools, and help
- **Toolbar**: Quick access to common functions
- **Project Tree**: Model components and data
- **Main Canvas**: Visualization area
- **Control Panels**: Parameter adjustment and settings
- **Status Bar**: Progress and messages

Creating a New Project
----------------------

1. Click **File → New Project**
2. Choose project type:
   - **2D Model**: Single layer subsurface model
   - **3D Model**: Multi-layer volumetric model
3. Set basic parameters:
   - Grid dimensions (nx, ny, nz)
   - Spatial extent (xmin, xmax, etc.)
   - Cell size (dx, dy, dz)

Loading Example Data
~~~~~~~~~~~~~~~~~~~~

1. Click **File → Load Example**
2. Select from available examples:
   - Ore Body (2D)
   - Magmatic Intrusion (3D)
   - Kimberlite Pipe
3. The model will load with pre-configured parameters

Importing Custom Data
~~~~~~~~~~~~~~~~~~~~~

**Density Models**
1. Click **Import → Density Model**
2. Select CSV file with density values
3. Specify grid dimensions and spacing
4. Choose coordinate system origin

**Observation Data**
1. Click **Import → Gravity Data**
2. Select CSV file with columns: x, y, z, gravity, uncertainty
3. Specify units and coordinate system

Model Visualization
-------------------

2D Visualization
~~~~~~~~~~~~~~~~

**Gravity Field Plot**
- Displays calculated gravity anomalies
- Color scale represents anomaly magnitude
- Interactive zoom and pan
- Export to image formats

**Density Cross-Section**
- Shows subsurface density distribution
- Vertical exaggeration control
- Profile extraction tools

3D Visualization
~~~~~~~~~~~~~~~~

**Volume Rendering**
- 3D density distribution
- Opacity and color mapping
- Interactive rotation and slicing
- Isosurface extraction

**Gravity Field Surfaces**
- 3D gravity anomaly surfaces
- Contour overlays
- Multiple viewpoint control

Interactive Tools
-----------------

Drawing Tools
~~~~~~~~~~~~~

**Polygon Drawing**
1. Select polygon tool
2. Click to define vertices
3. Double-click to close shape
4. Assign density value

**Rectangle/Circle Tools**
1. Click and drag to define shape
2. Adjust size and position
3. Set density properties

**Freehand Drawing**
1. Draw arbitrary shapes
2. Smooth and refine boundaries
3. Convert to density regions

Parameter Adjustment
~~~~~~~~~~~~~~~~~~~~

**Density Editor**
- Click on model regions
- Adjust density values
- Apply to multiple cells
- Preview changes

**Grid Refinement**
- Increase resolution in areas of interest
- Maintain computational efficiency
- Automatic interpolation

Calculations
------------

Forward Modeling
~~~~~~~~~~~~~~~~

1. Click **Calculate → Forward Model**
2. Choose calculation method:
   - **Direct Summation**: Exact calculation
   - **FFT Method**: Fast approximation
3. Set observation height
4. View progress and results

Inversion
~~~~~~~~~

1. Click **Calculate → Inversion**
2. Select inversion method:
   - **Linear Inversion**: Fast, approximate
   - **Nonlinear Inversion**: Accurate, slower
3. Set regularization parameters
4. Monitor convergence
5. View uncertainty estimates

Batch Processing
----------------

Processing Multiple Models
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Click **Batch → New Batch Job**
2. Add multiple project files
3. Configure processing parameters
4. Set output directory
5. Monitor progress
6. Review results summary

Parameter Studies
~~~~~~~~~~~~~~~~~

1. Define parameter ranges
2. Set up sensitivity analysis
3. Run automated calculations
4. Generate response surfaces
5. Statistical analysis of results

Data Export
-----------

Export Formats
~~~~~~~~~~~~~~

**Visualization**
- PNG/JPG images
- PDF vector graphics
- SVG scalable format

**Data Files**
- CSV numerical data
- JSON project files
- HDF5 binary format
- GeoTIFF geospatial

**Reports**
- HTML summary reports
- PDF technical reports
- Excel spreadsheets

Animation
~~~~~~~~~

Create time-lapse animations:

1. Set up parameter sequence
2. Configure animation settings
3. Preview animation
4. Export as MP4 or GIF

Advanced Features
-----------------

Uncertainty Analysis
~~~~~~~~~~~~~~~~~~~~

1. Click **Analysis → Uncertainty**
2. Define parameter uncertainties
3. Run Monte Carlo simulation
4. View probability distributions
5. Generate confidence intervals

Resolution Analysis
~~~~~~~~~~~~~~~~~~~

1. Click **Analysis → Resolution Matrix**
2. Compute model resolution
3. Visualize resolving kernels
4. Assess parameter trade-offs

Integration Tools
-----------------

**GIS Integration**
- Import shapefiles
- Export to GIS formats
- Coordinate system transformations

**Well Log Integration**
- Import borehole data
- Tie to seismic horizons
- Joint inversion capabilities

Keyboard Shortcuts
------------------

Common shortcuts:

- **Ctrl+N**: New project
- **Ctrl+O**: Open project
- **Ctrl+S**: Save project
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo
- **F5**: Recalculate
- **F9**: Toggle 3D view
- **Ctrl+P**: Print/plot

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Slow Performance**
- Reduce grid resolution
- Use FFT approximation
- Close other applications
- Increase RAM if possible

**Visualization Problems**
- Update graphics drivers
- Reset view settings
- Clear cache files
- Check OpenGL support

**Calculation Errors**
- Verify input data ranges
- Check coordinate systems
- Validate density values
- Review convergence settings

**Memory Issues**
- Process smaller models
- Use 64-bit Python
- Close unused applications
- Consider cloud computing

Getting Help
------------

**Built-in Help**
- Press F1 for context help
- Access user manual
- View tutorial videos

**Online Resources**
- Documentation website
- User forum
- Issue tracker
- Video tutorials

**Technical Support**
- Email support
- Live chat (business hours)
- Phone support (premium plans)
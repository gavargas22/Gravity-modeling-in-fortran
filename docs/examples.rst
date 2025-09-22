Examples
========

This section showcases the example datasets included with Gravity Modeling. Each example demonstrates different aspects of gravity modeling and serves as a starting point for your own projects.

Available Examples
------------------

Ore Body (2D)
~~~~~~~~~~~~~

A simple 2D model of a subsurface ore body with high density contrast.

**Location**: ``examples/ore_body_2d/``

**Features**:
- Single ore body at 200m depth
- Density contrast: 0.5 g/cm³
- Grid: 100x100 points
- Extent: 1000m x 1000m

.. code-block:: python

    from gmm import GravityModel

    # Load the example
    model = GravityModel.from_json('examples/ore_body_2d/project.json')

    # Calculate and visualize
    gravity = model.calculate_gravity()
    model.plot_2d_field()

**Physical Interpretation**:
This example shows how a compact, high-density ore body creates a positive gravity anomaly. The anomaly is strongest directly above the body and decreases with distance.

Intrusion (3D)
~~~~~~~~~~~~~

A 3D model of a magmatic intrusion with complex geometry.

**Location**: ``examples/intrusion_3d/``

**Features**:
- Irregular intrusion shape
- Variable density: 0.3-0.4 g/cm³
- Grid: 50x50x20 points
- Volume: ~1 million m³

.. code-block:: python

    # Load 3D example
    model = GravityModel.from_json('examples/intrusion_3d/project.json')

    # 3D visualization
    model.plot_3d_density()

**Physical Interpretation**:
Demonstrates how 3D structures create more complex gravity patterns. The irregular shape leads to asymmetric anomalies that can help constrain the intrusion's geometry.

Kimberlite Pipe
~~~~~~~~~~~~~~~

A model of a diamond-bearing kimberlite pipe, typical of diamond mining districts.

**Location**: ``examples/kimberlite_pipe/``

**Features**:
- Pipe-like geometry
- High density contrast: 0.8 g/cm³
- Depth extent: 500m
- Small surface expression

.. code-block:: python

    # Load kimberlite example
    model = GravityModel.from_json('examples/kimberlite_pipe/project.json')

    # Analyze the pipe signature
    gravity = model.calculate_gravity()
    print(f"Maximum anomaly: {gravity.max():.1f} mGal")
    print(f"Anomaly diameter: ~{model.estimate_anomaly_width()}m")

**Physical Interpretation**:
Kimberlite pipes often have subtle gravity signatures due to their small size and depth. This example shows how careful survey design is needed to detect these features.

Creating Custom Examples
------------------------

Template Structure
~~~~~~~~~~~~~~~~~~

All examples follow this structure::

    examples/
    └── your_example/
        ├── project.json          # Model configuration
        ├── inputs/
        │   ├── model_1.csv      # Density model
        │   └── input_data.csv   # Optional observation data
        └── outputs/
            └── OUTPUT.TXT       # Legacy format output

Project JSON Format
~~~~~~~~~~~~~~~~~~~

The ``project.json`` file defines the model parameters:

.. code-block:: json

    {
        "name": "My Custom Model",
        "description": "Description of the model",
        "nx": 100,
        "ny": 100,
        "nz": 1,
        "dx": 10.0,
        "dy": 10.0,
        "dz": 10.0,
        "xmin": 0.0,
        "ymin": 0.0,
        "zmin": 0.0,
        "density_file": "inputs/model_1.csv",
        "data_file": "inputs/input_data.csv"
    }

Data File Formats
~~~~~~~~~~~~~~~~~

**Density Model (CSV)**:
Comma-separated values with density in g/cm³::

    2.7,2.7,2.7,...
    2.7,3.2,3.2,...
    2.7,3.2,3.2,...

**Observation Data (CSV)**:
Columns: x, y, z, gravity, uncertainty::

    x,y,z,gravity,uncertainty
    100.0,100.0,0.0,5.2,0.1
    200.0,150.0,0.0,3.8,0.1

Running Examples in Batch
--------------------------

Process all examples automatically:

.. code-block:: python

    import glob
    from pathlib import Path
    import matplotlib.pyplot as plt

    # Process all examples
    project_files = glob.glob('examples/*/project.json')

    fig, axes = plt.subplots(1, len(project_files), figsize=(15, 5))

    for i, project_file in enumerate(project_files):
        model_name = Path(project_file).parent.name
        model = GravityModel.from_json(project_file)

        # Calculate gravity
        gravity = model.calculate_gravity()

        # Plot
        ax = axes[i] if len(project_files) > 1 else axes
        im = ax.imshow(gravity.T, origin='lower', cmap='viridis',
                      extent=[model.xmin, model.xmax, model.ymin, model.ymax])
        ax.set_title(f'{model_name.replace("_", " ").title()}')

    plt.tight_layout()
    plt.show()

Comparing Model Results
-----------------------

Analyze differences between models:

.. code-block:: python

    models = {}
    for project_file in project_files:
        name = Path(project_file).parent.name
        model = GravityModel.from_json(project_file)
        gravity = model.calculate_gravity()

        models[name] = {
            'model': model,
            'gravity': gravity,
            'max_anomaly': float(gravity.max()),
            'anomaly_area': float((gravity > gravity.mean() + gravity.std()).sum())
        }

    # Print comparison
    print("Model Comparison:")
    print("-" * 50)
    for name, data in models.items():
        print(f"{name:15}: Max {data['max_anomaly']:6.1f} mGal, "
              f"Area {data['anomaly_area']:4.0f} cells")

Validation and Testing
----------------------

Each example includes validation data:

.. code-block:: python

    # Load model and observations
    model = GravityModel.from_json('examples/ore_body_2d/project.json')

    if model.data_points:
        # Calculate at observation points
        calculated = model.calculate_gravity_at_points(model.data_points)
        observed = [p.gravity for p in model.data_points]

        # Compute RMS error
        rms_error = np.sqrt(np.mean((np.array(observed) - np.array(calculated))**2))
        print(f"RMS error: {rms_error:.2f} mGal")

        # Plot comparison
        plt.scatter(observed, calculated, alpha=0.7)
        plt.plot([min(observed), max(observed)], [min(observed), max(observed)],
                'r--', label='Perfect fit')
        plt.xlabel('Observed Gravity (mGal)')
        plt.ylabel('Calculated Gravity (mGal)')
        plt.title('Model Validation')
        plt.legend()
        plt.show()

Extending Examples
------------------

Create variations of existing examples:

1. **Modify density**: Change the density contrast to see its effect
2. **Change geometry**: Alter the shape or size of subsurface bodies
3. **Add noise**: Include measurement errors in observation data
4. **Multiple bodies**: Combine several anomalies in one model
5. **Complex geology**: Add multiple layers with different densities

Use these examples as templates for your own geophysical modeling projects!
Quick Start Guide
================

This guide will get you up and running with Gravity Modeling in minutes. We'll cover loading example data, running basic calculations, and creating your first visualization.

Loading Example Data
--------------------

The package includes several example datasets to help you get started:

.. code-block:: python

    from gmm import GravityModel

    # Load the 2D ore body example
    model = GravityModel.from_json('examples/ore_body_2d/project.json')

    # Display basic information
    print(f"Model: {model.name}")
    print(f"Grid size: {model.nx} x {model.ny}")
    print(f"Data points: {len(model.data_points)}")

Basic Gravity Calculation
-------------------------

Calculate the gravitational field for your model:

.. code-block:: python

    # Calculate gravity field
    gravity_field = model.calculate_gravity()

    # Print some statistics
    print(f"Gravity range: {gravity_field.min():.2f} to {gravity_field.max():.2f} mGal")
    print(f"Mean gravity: {gravity_field.mean():.2f} mGal")

2D Visualization
----------------

Create a simple 2D plot of the gravity field:

.. code-block:: python

    import matplotlib.pyplot as plt

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot gravity field
    im = ax.imshow(gravity_field.T, origin='lower', cmap='viridis',
                   extent=[model.xmin, model.xmax, model.ymin, model.ymax])

    # Add colorbar
    plt.colorbar(im, ax=ax, label='Gravity Anomaly (mGal)')

    # Add data points
    if model.data_points:
        x_obs, y_obs = zip(*[(p.x, p.y) for p in model.data_points])
        ax.scatter(x_obs, y_obs, c='red', s=50, label='Observations')
        ax.legend()

    # Labels and title
    ax.set_xlabel('X Distance (m)')
    ax.set_ylabel('Y Distance (m)')
    ax.set_title('Gravity Anomaly Map')

    plt.show()

Working with Data Points
------------------------

Add observation points and compare with calculated values:

.. code-block:: python

    from gmm import DataPoint

    # Add some observation points
    observations = [
        DataPoint(x=100, y=100, gravity=5.2),
        DataPoint(x=200, y=150, gravity=3.8),
        DataPoint(x=300, y=200, gravity=7.1),
    ]

    model.data_points = observations

    # Calculate residuals (observed - calculated)
    calculated = model.calculate_gravity_at_points(observations)
    residuals = [obs.gravity - calc for obs, calc in zip(observations, calculated)]

    print("Residuals (mGal):")
    for i, res in enumerate(residuals):
        print(f"Point {i+1}: {res:.2f}")

3D Visualization
----------------

For 3D models, create subsurface visualizations:

.. code-block:: python

    # Assuming a 3D model
    if hasattr(model, 'nz') and model.nz > 1:
        fig = plt.figure(figsize=(12, 8))

        # Create 3D subplot
        ax = fig.add_subplot(111, projection='3d')

        # Plot subsurface density
        X, Y, Z = np.meshgrid(model.x_coords, model.y_coords, model.z_coords)
        ax.scatter(X.flatten(), Y.flatten(), Z.flatten(),
                  c=model.density.flatten(), cmap='coolwarm', alpha=0.6)

        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Depth (m)')
        ax.set_title('3D Density Distribution')

        plt.show()

Batch Processing
----------------

Process multiple models automatically:

.. code-block:: python

    import glob
    from pathlib import Path

    # Find all project files
    project_files = glob.glob('examples/*/project.json')

    results = {}
    for project_file in project_files:
        model_name = Path(project_file).parent.name

        # Load and process
        model = GravityModel.from_json(project_file)
        gravity = model.calculate_gravity()

        results[model_name] = {
            'model': model,
            'gravity_field': gravity,
            'stats': {
                'min': float(gravity.min()),
                'max': float(gravity.max()),
                'mean': float(gravity.mean()),
                'std': float(gravity.std())
            }
        }

        print(f"Processed {model_name}: {results[model_name]['stats']}")

Saving Results
--------------

Save your work for later use:

.. code-block:: python

    # Save model with results
    model.save_project('my_results.json')

    # Export gravity field as CSV
    import pandas as pd

    df = pd.DataFrame({
        'x': np.repeat(model.x_coords, len(model.y_coords)),
        'y': np.tile(model.y_coords, len(model.x_coords)),
        'gravity': gravity_field.flatten()
    })

    df.to_csv('gravity_field.csv', index=False)

Next Steps
----------

Now that you know the basics:

1. **Explore the GUI**: Run ``python -m src.gravity_modeling_app`` for interactive modeling
2. **Try different examples**: Check out all the example datasets in the ``examples/`` folder
3. **Learn the API**: See the :doc:`api_reference` for detailed documentation
4. **Customize models**: Modify parameters and see how they affect results
5. **Run inversions**: Use the inversion module to estimate subsurface properties

For more advanced usage, check out the :doc:`examples` and :doc:`theory` sections.
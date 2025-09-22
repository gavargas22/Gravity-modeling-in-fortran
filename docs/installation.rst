Installation
============

System Requirements
-------------------

- Python 3.8 or higher
- Windows 10+, macOS 10.15+, or Linux
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space

Dependencies
------------

The package requires the following Python packages:

**Core Dependencies:**
- numpy: Numerical computing
- scipy: Scientific computing
- pandas: Data manipulation
- matplotlib: Plotting and visualization
- pint: Physical units

**GUI Dependencies:**
- PySide6: Qt-based GUI framework

**Development Dependencies:**
- pytest: Testing framework
- sphinx: Documentation generation
- pyinstaller: Executable creation

Installation Methods
--------------------

Method 1: Using uv (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

uv is a fast Python package manager that handles virtual environments automatically::

    # Clone the repository
    git clone https://github.com/your-repo/gravity-modeling.git
    cd gravity-modeling

    # Install dependencies
    uv install

    # Install in development mode
    uv pip install -e .

Method 2: Using pip
~~~~~~~~~~~~~~~~~~~

If you prefer using pip::

    # Clone the repository
    git clone https://github.com/your-repo/gravity-modeling.git
    cd gravity-modeling

    # Create virtual environment
    python -m venv venv
    venv\Scripts\activate  # Windows
    # source venv/bin/activate  # macOS/Linux

    # Install dependencies
    pip install -r requirements.txt

    # Install in development mode
    pip install -e .

Method 3: Using conda
~~~~~~~~~~~~~~~~~~~~~

For conda users::

    # Create environment
    conda create -n gravity-modeling python=3.9
    conda activate gravity-modeling

    # Install dependencies
    conda install numpy scipy pandas matplotlib pyside6 pint pytest

    # Clone and install
    git clone https://github.com/your-repo/gravity-modeling.git
    cd gravity-modeling
    pip install -e .

Verification
------------

After installation, verify everything works::

    python -c "import gmm; print('Gravity Modeling installed successfully!')"

Launch the GUI::

    python -m src.gravity_modeling_app

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import Error: No module named 'gmm'**

- Ensure you're in the correct directory
- Check that the package is installed: ``pip list | grep gmm``
- Try reinstalling: ``pip install -e .``

**GUI Won't Start**

- Ensure PySide6 is installed: ``pip install PySide6``
- Check your display environment (especially on Linux)
- Try running with ``QT_DEBUG_PLUGINS=1`` for debug info

**Memory Errors**

- Increase available RAM
- Process smaller datasets
- Close other memory-intensive applications

**Performance Issues**

- Use numpy/scipy compiled with optimized BLAS/LAPACK
- Consider using conda-forge packages for better performance
- For large datasets, use batch processing mode

Development Setup
-----------------

For contributors and developers::

    # Install development dependencies
    uv add --dev pytest sphinx pyinstaller

    # Run tests
    pytest

    # Build documentation
    cd docs && make html

    # Build executable
    pyinstaller --onefile src/gravity_modeling_app.py
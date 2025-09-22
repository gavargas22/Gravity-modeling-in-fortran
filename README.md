# Gravity-modeling-in-fortran

Computer code written in about 1980 that needs to be updated. This project is undergoing modernization to replace legacy Fortran code with a modern Python implementation and PySide6 GUI.

## Project Status

### ✅ Completed
- **Complete Python Translation**: Fortran algorithms translated to Python (inversion, forward modeling)
- **Modern GUI**: PySide6-based interface replacing Gooey
- **Data Management**: Enhanced project loading and geometry handling
- **API Layer**: Clean separation between GUI and computation with progress reporting
- **Parameter Adjustment**: Iterative parameter optimization implemented
- **Project Serialization**: Save/load project functionality with validation

### 🚧 In Progress
- **Visualization**: Adding matplotlib plots for data and model visualization
- **Validation**: Comparing Python results with original Fortran outputs
- **Advanced Features**: 3D model visualization and batch processing

## Installation

1. Install uv (Python package manager):
   ```bash
   # On Windows
   powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Create virtual environment and install dependencies:
   ```bash
   uv venv --python 3.13
   .venv\Scripts\activate  # On Windows
   uv pip install -r requirements.txt
   ```

## Usage

### Modern GUI Application
```bash
python src/gravity_modeling_app.py
```

Features:
- **Project Management**: Create, load, save, and validate projects
- **Interactive Parameter Editing**: Real-time adjustment of model parameters
- **Inversion Controls**: Configurable iterations with/without parameter adjustment
- **Progress Monitoring**: Real-time progress updates during inversion
- **Results Visualization**: Parameter tables and inversion statistics
- **Data Validation**: Comprehensive project validation with error reporting

### Programmatic API
```python
from gmm.api import GravityModelingAPI

api = GravityModelingAPI()
result = api.load_project("models/test1/test1.json")
api.run_inversion(iterations=10, enable_parameter_adjustment=True)
```

### Legacy Fortran Build (deprecated)
```bash
python -m numpy.f2py -c inver.f svd.f talw.f rotate.f -m inver
```

## Project Structure

```
src/
├── gravity_modeling_app.py    # Modern PySide6 GUI with API integration
├── gmm/
│   ├── api.py                 # API layer for computation/GUI separation
│   ├── gm.py                  # Enhanced model class with validation
│   ├── inversion_complete.py  # Python inversion algorithm
│   └── talw.py                # Field calculation functions
models/
├── test1/                     # Test project data
└── .agentic-docs/
    └── modernization_plan.md   # Detailed modernization plan
```

## Development

The project uses modern Python development practices:
- **uv** for dependency management
- **pytest** for testing
- **Git branches** for feature development
- **Type hints** and documentation

## Migration from Fortran

The original Fortran code has been fully translated to Python while maintaining algorithmic fidelity. Key improvements:

- **Maintainability**: Python is easier to modify and extend
- **Integration**: Seamless integration with scientific Python ecosystem
- **Performance**: NumPy provides competitive performance
- **Usability**: Modern GUI with interactive features
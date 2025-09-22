# Legacy Fortran Code

This directory contains the original Fortran source files that have been fully translated to Python.

## Files

- `inver.f` - Main inversion algorithm (translated to `src/gmm/inversion_complete.py`)
- `talw.f` - Field calculation functions (translated to `src/gmm/talw.py`)
- `svd.f` - SVD decomposition routines
- `rotate.f` - Coordinate rotation functions
- `main.f` - Main program entry point
- `mod1.f` - Model definitions and utilities
- `plot.f` - Plotting routines

## Status

These files are kept for reference and historical purposes only. The active codebase uses the Python translations in the `src/` directory, which provide the same functionality with improved maintainability and modern features.

## Translation Notes

The Python translation includes:
- Full algorithm preservation
- Enhanced error handling
- Progress reporting
- Parameter validation
- Modern Python APIs
- Integration with PySide6 GUI
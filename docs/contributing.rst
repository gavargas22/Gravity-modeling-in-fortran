Contributing
============

This document outlines how to contribute to the Gravity Modeling project.

Development Setup
-----------------

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a virtual environment: ``python -m venv venv``
4. Activate the environment: ``venv\Scripts\activate`` (Windows) or ``source venv/bin/activate`` (Linux/Mac)
5. Install dependencies: ``pip install -r requirements.txt``
6. Install development dependencies: ``pip install pytest sphinx``

Code Style
----------

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep line lengths under 88 characters

Testing
-------

- Write unit tests for new functionality
- Ensure all tests pass before submitting a pull request
- Run tests with: ``python -m pytest``

Documentation
-------------

- Update documentation for any new features
- Build documentation locally: ``cd docs && sphinx-build . _build/html``
- Check that documentation builds without warnings

Submitting Changes
------------------

1. Create a feature branch from ``main``
2. Make your changes
3. Write tests and documentation
4. Ensure all tests pass and documentation builds
5. Submit a pull request with a clear description of changes
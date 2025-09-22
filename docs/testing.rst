Testing
=======

This document describes the testing framework and procedures for the Gravity Modeling project.

Running Tests
-------------

To run the test suite::

    python -m pytest

For verbose output::

    python -m pytest -v

For coverage report::

    python -m pytest --cov=gmm --cov-report=html

Test Structure
--------------

Tests are organized in the ``tests/`` directory with the following structure:

- ``test_gm.py`` - Tests for the core GMModel class
- ``test_inversion.py`` - Tests for inversion algorithms
- ``test_api.py`` - Tests for the API endpoints
- ``test_gui.py`` - Tests for GUI components (if applicable)

Writing Tests
-------------

- Use descriptive test names that explain what is being tested
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common test setup
- Mock external dependencies when appropriate

Example test::

    def test_gm_model_initialization():
        model = GMModel(new_project=True)
        assert model.project_name == "New Project"
        assert model.is_valid == False

Continuous Integration
----------------------

Tests are automatically run on GitHub Actions for all pull requests and pushes to main.

Test Coverage
-------------

We aim for high test coverage (>80%) for all core functionality. Coverage reports are generated automatically and available in the GitHub Actions artifacts.
"""
Type definitions and data classes for the GMM package
"""

from dataclasses import dataclass


@dataclass
class InversionProgress:
    """Data class for inversion progress reporting"""
    iteration: int
    max_iterations: int
    chi_squared: float
    parameters_updated: int
    message: str
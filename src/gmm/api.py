"""
API layer for Gravity/Magnetics Modeling
Provides clean separation between GUI and computation logic
"""

from typing import Optional, Callable, Dict, Any
from pathlib import Path
import numpy as np
from .gm import GMModel
from .types import InversionProgress


class GravityModelingAPI:
    """API for gravity and magnetics modeling operations"""

    def __init__(self):
        self.current_model: Optional[GMModel] = None
        self.progress_callback: Optional[Callable[[InversionProgress], None]] = None

    def load_project(self, project_path: str) -> Dict[str, Any]:
        """Load a project and return status information"""
        try:
            self.current_model = GMModel(
                project_file=project_path,
                new_project=False,
                progress_callback=self.progress_callback
            )

            if self.current_model.is_valid:
                return {
                    "success": True,
                    "message": f"Loaded project: {self.current_model.project_name}",
                    "project_info": self.get_project_info()
                }
            else:
                return {
                    "success": False,
                    "message": "Project loaded with validation errors",
                    "errors": self.current_model.validation_errors,
                    "project_info": self.get_project_info() if self.current_model else None
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to load project: {str(e)}",
                "errors": [str(e)],
                "project_info": None
            }

    def create_new_project(self, name: str, **kwargs) -> Dict[str, Any]:
        """Create a new project"""
        try:
            self.current_model = GMModel(new_project=True, **kwargs)
            self.current_model.project_name = name

            return {
                "success": True,
                "message": f"Created new project: {name}",
                "project_info": self.get_project_info()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create project: {str(e)}",
                "errors": [str(e)],
                "project_info": None
            }

    def save_project(self, filepath: Optional[str] = None) -> Dict[str, Any]:
        """Save the current project"""
        if not self.current_model:
            return {
                "success": False,
                "message": "No project loaded",
                "errors": ["No project loaded"]
            }

        try:
            save_path = filepath or self.current_model.project_file
            success = self.current_model.save_project(save_path)

            if success:
                return {
                    "success": True,
                    "message": f"Project saved to {save_path}",
                    "filepath": save_path
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save project",
                    "errors": self.current_model.validation_errors
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error saving project: {str(e)}",
                "errors": [str(e)]
            }

    def run_inversion(self, iterations: int = 10, **kwargs) -> Dict[str, Any]:
        """Run inversion with progress reporting"""
        if not self.current_model:
            return {
                "success": False,
                "message": "No project loaded",
                "errors": ["No project loaded"]
            }

        if not self.current_model.is_valid:
            return {
                "success": False,
                "message": "Project has validation errors",
                "errors": self.current_model.validation_errors
            }

        try:
            # Run inversion
            self.current_model.inversion(iterations=iterations, **kwargs)

            return {
                "success": True,
                "message": "Inversion completed successfully",
                "results": self.get_inversion_results()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Inversion failed: {str(e)}",
                "errors": [str(e)]
            }

    def get_project_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current project"""
        if not self.current_model:
            return None

        return {
            "name": self.current_model.project_name,
            "modeling_mode": self.current_model.modeling_mode,
            "stations": self.current_model.nstat,
            "polygons": self.current_model.npoly,
            "ambient_field": self.current_model.ambient_field,
            "inclination": self.current_model.inclination,
            "azimuth": self.current_model.azimuth,
            "units": self.current_model.units,
            "is_valid": self.current_model.is_valid,
            "validation_errors": self.current_model.validation_errors
        }

    def get_model_parameters(self) -> Optional[Dict[str, Any]]:
        """Get current model parameters"""
        if not self.current_model:
            return None

        polygons = []
        for i in range(self.current_model.npoly):
            polygons.append({
                "id": i + 1,
                "density": float(self.current_model.densty[i]),
                "susceptibility": float(self.current_model.suscp[i]),
                "strike_length": float(self.current_model.sl[i]),
                "vertices": int(self.current_model.nsides[i] + 1)
            })

        return {
            "polygons": polygons,
            "total_polygons": self.current_model.npoly
        }

    def update_model_parameters(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update model parameters"""
        if not self.current_model:
            return {
                "success": False,
                "message": "No project loaded",
                "errors": ["No project loaded"]
            }

        try:
            # Update polygon parameters
            if "polygons" in updates:
                for poly_update in updates["polygons"]:
                    poly_id = poly_update.get("id", 0) - 1  # Convert to 0-based
                    if 0 <= poly_id < self.current_model.npoly:
                        if "density" in poly_update:
                            self.current_model.densty[poly_id] = poly_update["density"]
                        if "susceptibility" in poly_update:
                            self.current_model.suscp[poly_id] = poly_update["susceptibility"]
                        if "strike_length" in poly_update:
                            self.current_model.sl[poly_id] = poly_update["strike_length"]

            # Update project settings
            project_fields = ["ambient_field", "inclination", "azimuth", "modeling_mode"]
            for field in project_fields:
                if field in updates:
                    setattr(self.current_model, field, updates[field])
                    # Recalculate magnetic field components if needed
                    if field in ["ambient_field", "inclination", "azimuth", "modeling_mode"]:
                        self.current_model.calculate_magnetic_field_components()

            return {
                "success": True,
                "message": "Parameters updated successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to update parameters: {str(e)}",
                "errors": [str(e)]
            }

    def get_measurement_data(self) -> Optional[Dict[str, Any]]:
        """Get measurement data for plotting"""
        if not self.current_model or not hasattr(self.current_model, 'measurements'):
            return None

        df = self.current_model.measurements
        return {
            "stations": df['station'].tolist() if 'station' in df.columns else list(range(len(df))),
            "distance": df['distance'].tolist(),
            "observed_gravity": df['obs_grav'].tolist(),
            "observed_magnetic": df['obs_mag'].tolist(),
            "elevation": df.get('elev', [0] * len(df)).tolist()
        }

    def get_inversion_results(self) -> Optional[Dict[str, Any]]:
        """Get inversion results"""
        if not self.current_model:
            return None

        # Calculate current model response
        try:
            # This would need to be implemented to compute current model response
            # For now, return basic parameter info
            return {
                "polygons": self.get_model_parameters()["polygons"],
                "chi_squared": getattr(self.current_model, 'last_chi_squared', None),
                "iterations_completed": getattr(self.current_model, 'iterations_completed', 0)
            }
        except:
            return self.get_model_parameters()

    def set_progress_callback(self, callback: Callable[[InversionProgress], None]):
        """Set progress callback function"""
        self.progress_callback = callback
        if self.current_model:
            self.current_model.progress_callback = callback

    def validate_project(self) -> Dict[str, Any]:
        """Validate the current project"""
        if not self.current_model:
            return {
                "valid": False,
                "message": "No project loaded",
                "errors": ["No project loaded"]
            }

        return {
            "valid": self.current_model.is_valid,
            "message": self.current_model.get_validation_report(),
            "errors": self.current_model.validation_errors
        }
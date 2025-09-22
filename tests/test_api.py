#!/usr/bin/env python3
"""
Test script for the Gravity Modeling API
Use this with the VS Code debug configuration "Python: API Test"
"""

from gmm.api import GravityModelingAPI


def test_api_functionality():
    """Test the main API functionality"""
    print("Testing Gravity Modeling API...")

    # Create API instance
    api = GravityModelingAPI()
    print("✓ API instance created")

    # Test project loading
    print("\nLoading test project...")
    result = api.load_project("models/test1/test1.json")
    if result["success"]:
        print("✓ Project loaded successfully")
        print(f"  - Project: {result['project_info']['name']}")
        print(f"  - Stations: {result['project_info']['stations']}")
        print(f"  - Polygons: {result['project_info']['polygons']}")
    else:
        print("✗ Failed to load project:")
        for error in result.get("errors", []):
            print(f"  - {error}")
        return

    # Test parameter retrieval
    print("\nTesting parameter retrieval...")
    params = api.get_model_parameters()
    if params:
        print("✓ Parameters retrieved")
        print(f"  - Total polygons: {params['total_polygons']}")
        for poly in params['polygons'][:2]:  # Show first 2 polygons
            print(f"  - Polygon {poly['id']}: ρ={poly['density']:.3f}, χ={poly['susceptibility']:.3f}")
    else:
        print("✗ Failed to retrieve parameters")

    # Test forward modeling (no parameter adjustment)
    print("\nTesting forward modeling (no parameter adjustment)...")
    result = api.run_inversion(iterations=3, enable_parameter_adjustment=False)
    if result["success"]:
        print("✓ Forward modeling completed")
        if "results" in result and result["results"]:
            print(f"  - Final Chi²: {result['results'].get('chi_squared', 'N/A')}")
    else:
        print("✗ Forward modeling failed:")
        for error in result.get("errors", []):
            print(f"  - {error}")

    # Test parameter adjustment
    print("\nTesting parameter adjustment...")
    result = api.run_inversion(iterations=3, enable_parameter_adjustment=True)
    if result["success"]:
        print("✓ Parameter adjustment completed")
        if "results" in result and result["results"]:
            print(f"  - Final Chi²: {result['results'].get('chi_squared', 'N/A')}")
            # Show updated parameters
            updated_params = api.get_model_parameters()
            if updated_params:
                print("  - Updated parameters:")
                for poly in updated_params['polygons'][:2]:  # Show first 2 polygons
                    print(f"    Polygon {poly['id']}: ρ={poly['density']:.3f}, χ={poly['susceptibility']:.3f}")
    else:
        print("✗ Parameter adjustment failed:")
        for error in result.get("errors", []):
            print(f"  - {error}")

    # Test parameter updates
    print("\nTesting parameter updates...")
    updates = {
        "polygons": [
            {"id": 1, "density": -0.25, "susceptibility": 0.001}
        ]
    }
    result = api.update_model_parameters(updates)
    if result["success"]:
        print("✓ Parameters updated successfully")
        # Verify the update
        params = api.get_model_parameters()
        if params and params['polygons']:
            poly1 = next((p for p in params['polygons'] if p['id'] == 1), None)
            if poly1:
                print(f"  - Polygon 1: ρ={poly1['density']:.3f}, χ={poly1['susceptibility']:.3f}")
    else:
        print("✗ Parameter update failed:")
        for error in result.get("errors", []):
            print(f"  - {error}")

    # Test project validation
    print("\nTesting project validation...")
    result = api.validate_project()
    if result["valid"]:
        print("✓ Project validation passed")
    else:
        print("✗ Project validation failed:")
        print(f"  - {result.get('message', 'Unknown error')}")

    print("\n🎉 API testing completed!")


def test_progress_callback():
    """Test the progress callback functionality"""
    print("\nTesting progress callback...")

    def progress_callback(progress):
        print(f"Progress: Iteration {progress.iteration}/{progress.max_iterations} - {progress.message}")

    api = GravityModelingAPI()
    api.set_progress_callback(progress_callback)

    result = api.load_project("models/test1/test1.json")
    if result["success"]:
        print("Running inversion with progress reporting...")
        api.run_inversion(iterations=2, enable_parameter_adjustment=True)
        print("✓ Progress callback test completed")
    else:
        print("✗ Failed to load project for progress test")


if __name__ == "__main__":
    print("Gravity Modeling API Debug Test")
    print("=" * 40)

    test_api_functionality()
    test_progress_callback()

    print("\n" + "=" * 40)
    print("Debug test completed. Check output above for results.")
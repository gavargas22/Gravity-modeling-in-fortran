# Gravity Modeling Examples

This directory contains realistic test data examples for the gravity modeling application. Each example includes complete project files with stations, observed data, and model geometry.

## Available Examples

### 1. Ore Body 2D (`ore_body_2d/`)
**File**: `ore_body_2d.json`

A simple 2D gravity profile example featuring:
- **14 stations** along a 650m profile (50m spacing)
- **Gravity data only** with realistic noise (0.1 mGal error)
- **2 polygons**: Background host rock + high-density ore body
- **Realistic parameters**: 150-200m depth, density contrast 0.8 g/cm³
- **Perfect for**: Learning basic gravity modeling, testing 2D inversion

**Key Features**:
- Clear gravity anomaly with Gaussian-like shape
- Single parameter to invert (ore body density)
- Quick convergence for testing algorithms

### 2. Magmatic Intrusion 3D (`intrusion_3d/`)
**File**: `intrusion_3d.json`

A complex 3D survey example featuring:
- **36 stations** in a 3x9 grid (100m spacing)
- **Gravity data only** with realistic noise (0.2 mGal error)
- **3 polygons**: Sedimentary basin + main intrusion + satellite body
- **Realistic parameters**: 100-300m depth, multiple density contrasts
- **Perfect for**: Testing 3D inversion, parameter correlation

**Key Features**:
- Multiple anomalous bodies with different signatures
- Grid station coverage for proper 3D modeling
- Mixed fixed and adjustable parameters
- Good test for convergence and stability

### 3. Kimberlite Pipe (`kimberlite_pipe/`)
**File**: `kimberlite_pipe.json`

An advanced example with both gravity and magnetic data:
- **31 stations** in a survey grid (50m spacing)
- **Dual data types**: Gravity (0.1 mGal error) + Magnetic (5 nT error)
- **3 polygons**: Country rock + kimberlite pipe + associated dike
- **Realistic parameters**: 200-400m depth, distinctive carrot-shaped pipe
- **Perfect for**: Testing joint inversion, complex geometries

**Key Features**:
- Kimberlite pipe with realistic carrot shape (narrowing with depth)
- Both gravity and magnetic anomalies
- Complex 3D geometry with multiple bodies
- Good test for multi-parameter inversion

## Using the Examples

### Loading in the Application
1. Start the gravity modeling application
2. Click "Load Project"
3. Navigate to `examples/[example_name]/[example_name].json`
4. The project will load with all stations, data, and model geometry

### Testing Inversion
- **Forward modeling**: Run with parameter adjustment disabled to see calculated data
- **Parameter adjustment**: Enable to invert for unknown densities/susceptibilities
- **Compare results**: Check how well the inversion recovers the true model parameters

### Expected Results
Each example is designed with realistic parameters that should produce:
- **Stable inversion convergence** within 10-20 iterations
- **Good data fit** (Chi-squared reduction)
- **Reasonable parameter recovery** (within uncertainty bounds)

## Parameter Realism

### Physical Units
- **Density**: g/cm³ (typical range: 2.0-5.0 for rocks, ores)
- **Gravity**: mGal (milligals, 1 mGal = 10⁻⁵ m/s²)
- **Magnetic**: nT (nanotesla, 1 nT = 10⁻⁹ T)
- **Susceptibility**: SI units (dimensionless, typical range: 0.0001-0.01)

### Geological Realism
- **Depths**: 100-500m (near-surface exploration targets)
- **Body sizes**: 50-200m (realistic for ore bodies, intrusions)
- **Density contrasts**: 0.1-1.0 g/cm³ (detectable gravity anomalies)
- **Magnetic contrasts**: 0.001-0.01 SI (detectable magnetic anomalies)

### Survey Design
- **Station spacing**: 25-100m (economic for ground surveys)
- **Survey area**: 200-800m (realistic exploration blocks)
- **Data quality**: Realistic noise levels based on instrument precision

## Creating Your Own Examples

Use these examples as templates for your own test data:

1. **Copy an existing example** as a starting point
2. **Modify station locations** for your survey geometry
3. **Adjust polygon vertices** for your geological model
4. **Set realistic density/susceptibility** values
5. **Generate synthetic data** using forward modeling
6. **Add noise** to simulate real measurement errors

## Validation

These examples have been validated to:
- ✅ Load correctly in the application
- ✅ Run forward modeling without errors
- ✅ Converge during parameter adjustment
- ✅ Produce realistic geophysical anomalies
- ✅ Test both 2D and 3D modeling capabilities
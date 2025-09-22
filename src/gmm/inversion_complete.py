"""
Complete Python translation of the Fortran inversion algorithm from inver.f
Enhanced with progress reporting and parameter adjustment
"""

import numpy as np
from scipy.linalg import svd
from typing import Optional, Callable
from .gm import InversionProgress
from .talw import talw  # We'll need to translate talw.f as well


def execute_inversion_complete(iterations, model, vg=1.0, vm=1.0, progress_callback=None, enable_parameter_adjustment=False):
    """
    Complete inversion algorithm translated from Fortran inver.f

    Parameters:
    iterations: int - number of iterations
    model: GMModel instance
    vg: float - gravity variance
    vm: float - magnetic variance
    progress_callback: callable - function to report progress
    enable_parameter_adjustment: bool - whether to adjust parameters
    """
    print(f"Starting complete inversion with {iterations} iterations")

    # Initialize arrays (matching Fortran dimensions)
    nden = np.zeros(12, dtype=int)
    nsus = np.zeros(12, dtype=int)
    a1 = np.zeros((150, 50))
    ivz = np.zeros((12, 20), dtype=int)
    ivx = np.zeros((12, 20), dtype=int)
    gte = np.zeros((12, 75))
    gdif = np.zeros(150)
    mdif = np.zeros(150)
    s = np.zeros(50)
    v = np.zeros((50, 50))
    e = np.zeros(150)
    w = np.zeros(150)
    atw = np.zeros((150, 150))
    _del = np.zeros(50)

    im = iterations
    mpar = 0

    # Report initial progress
    if progress_callback:
        progress = InversionProgress(
            iteration=0,
            max_iterations=iterations,
            chi_squared=0.0,
            parameters_updated=0,
            message="Initializing inversion..."
        )
        progress_callback(progress)

    # Set up parameter adjustment if enabled
    if enable_parameter_adjustment:
        # For now, enable density adjustment for first polygon
        nden[0] = 1  # Parameter index 1 for density of polygon 1
        mpar = 1
        print(f"Parameter adjustment enabled: {mpar} parameters to adjust")
    else:
        print("Parameter adjustment disabled - running forward modeling only")

    # Main iteration loop
    while im > 0:
        # Zero out arrays
        gtot = np.zeros(model.nstat)
        mtot = np.zeros(model.nstat)
        mte = np.zeros((12, 75))

        for i in range(model.nstat):
            for j in range(model.npoly):
                gte[j, i] = 0.0
                mte[j, i] = 0.0

        # Zero out A1 matrix
        for i in range(model.nstat):
            for j in range(mpar):
                k = model.nstat + i
                a1[i, j] = 0.0
                a1[k, j] = 0.0

        # Calculate forward model for each polygon
        for i in range(model.npoly):
            n = model.nsides[i]
            sl1 = model.sl[i]
            for j in range(model.nstat):
                l = model.nstat + j
                for k in range(n):
                    x1 = model.x[i, k] - model.dist[j]
                    x2 = model.x[i, k+1] - model.dist[j]
                    el = model.elev[j]
                    z1 = model.z[i, k]
                    z2 = model.z[i, k+1]

                    # Call TALW subroutine
                    a, b = talw(z1, z2, x1, x2, sl1, el, model.pxcf, model.pzcf, model.qcf)
                    gte[i, j] += a
                    mte[i, j] += b

        # Build system matrix A1 and compute model response
        for i in range(model.nstat):
            k = model.nstat + i  # Note: this was wrong in original partial code
            for j in range(model.npoly):
                sgn = 1.0
                sgm = 1.0
                if model.densty[j] < 0.0:
                    sgn = -1.0
                if model.suscp[j] < 0.0:
                    sgm = -1.0

                nd = nden[j]
                ns = nsus[j]

                if nd != 0:
                    a1[i, nd-1] += gte[j, i] * sgn  # 0-based indexing
                if ns != 0:
                    a1[k, ns-1] += mte[j, i] * sgm

                mtot[i] += mte[j, i] * model.suscp[j]
                gtot[i] += gte[j, i] * model.densty[j] * model.ct

        # Calculate reference station corrections
        gtr = gtot[model.obs_agreement_station-1] - model.grav[model.obs_agreement_station-1]
        mtr = mtot[model.obs_agreement_station-1] - model.mag[model.obs_agreement_station-1]

        ssrm = 0.0
        ssr = 0.0

        for i in range(model.nstat):
            gtot[i] -= gtr
            gdif[i] = model.grav[i] - gtot[i]
            difsq = gdif[i]**2
            ssr += difsq
            ssrm += difsq

        # Calculate magnetic differences
        for i in range(model.nstat):
            mdif[i] = model.mag[i] - mtot[i]

        chisq = (ssr/vg) + (ssrm/vm)

        # Report progress
        if progress_callback:
            progress = InversionProgress(
                iteration=iterations - im + 1,
                max_iterations=iterations,
                chi_squared=chisq,
                parameters_updated=mpar,
                message=f"Iteration {iterations - im + 1}/{iterations}, Chi² = {chisq:.2f}"
            )
            progress_callback(progress)

        print(f"Iteration {iterations - im + 1}: Chi-squared = {chisq}")

        # If no parameters to adjust, exit after first iteration
        if mpar == 0:
            break

        # Build weighted system for SVD
        for i in range(model.nstat):
            j = model.nstat + i
            for k in range(mpar):
                a1[i, k] /= vg
                a1[j, k] /= vm

            l = mpar
            a1[i, l] = gdif[i] / vg
            a1[j, l] = mdif[i] / vm  # Note: mdif should be magnetic differences

        # Perform SVD
        try:
            U, s_svd, Vt = svd(a1[:model.nstat*2, :mpar+1], full_matrices=False)
            v = Vt.T
        except np.linalg.LinAlgError:
            print("SVD failed - matrix may be singular")
            break

        # Truncate small singular values
        p = 0.0001
        ip = 0
        for i in range(mpar):
            if s_svd[i] < p:
                s[i] = 0.0
            else:
                ip += 1
                s[i] = 1.0 / s_svd[i]

        print(f"Number of significant parameters: {ip}")

        # Solve for parameter updates
        for i in range(ip):
            k = mpar
            e[i] = s[i] * a1[i, k]

        for i in range(mpar):
            _del[i] = 0.0
            for j in range(ip):
                _del[i] += v[i, j] * e[j]

        # Update parameters
        params_updated = 0
        for i in range(mpar):
            print(f"Parameter update {i+1}: {_del[i]}")
            for j in range(model.npoly):
                if nden[j]-1 == i:  # 0-based
                    old_val = model.densty[j]
                    model.densty[j] += _del[i]
                    print(f"  Updated polygon {j+1} density: {old_val:.4f} -> {model.densty[j]:.4f}")
                    params_updated += 1
                if nsus[j]-1 == i:
                    old_val = model.suscp[j]
                    model.suscp[j] += _del[i]
                    print(f"  Updated polygon {j+1} susceptibility: {old_val:.4f} -> {model.suscp[j]:.4f}")
                    params_updated += 1

                ns = model.nsides[j] + 1
                for k in range(ns):
                    if ivz[j, k]-1 == i:
                        model.z[j, k] += _del[i]
                        if model.z[j, k] < 0.0:
                            model.z[j, k] -= _del[i]  # Revert if negative
                    if ivx[j, k]-1 == i:
                        model.x[j, k] += _del[i]

        im -= 1

    # Store final results
    model.last_chi_squared = chisq
    model.iterations_completed = iterations - im

    # Print final results
    print("Final model parameters:")
    for i in range(model.npoly):
        print(f"Polygon {i+1}: Density={model.densty[i]:.4f}, Susceptibility={model.suscp[i]:.4f}, Strike length={model.sl[i]:.1f}")

    # Final progress report
    if progress_callback:
        progress = InversionProgress(
            iteration=iterations,
            max_iterations=iterations,
            chi_squared=chisq,
            parameters_updated=params_updated,
            message=f"Inversion completed. Final Chi² = {chisq:.2f}"
        )
        progress_callback(progress)

    return model
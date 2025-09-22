"""
Translation of TALW subroutine from talw.f
Calculates gravitational and magnetic field integrals for polygon sides
"""

import numpy as np


def talw(z1, z2, x1, x2, y1, el):
    """
    Calculate the integral over one side of a polygon with finite strike length

    Parameters:
    z1, z2: float - depths of endpoints
    x1, x2: float - horizontal distances of endpoints
    y1: float - strike length
    el: float - elevation

    Returns:
    a: float - gravity integral contribution
    b: float - magnetic integral contribution
    """
    # Get magnetic field components from common block (would be passed as parameters)
    # For now, use placeholder values - these should come from the model
    pxcf = 1.0  # Placeholder
    pzcf = 0.0  # Placeholder
    qcf = 1.0   # Placeholder

    ysq = y1 * y1
    zmag1 = z1 + el
    zmag2 = z2 + el
    vr1 = np.sqrt(x1**2 + ysq + zmag1**2)
    vr2 = np.sqrt(x2**2 + ysq + zmag2**2)

    a = 0.0
    b = 0.0
    nck = 0

    if abs(x1 - x2) < 0.001:
        nck = 1

    # Avoid division by zero
    if abs(x1) < 1e-5:
        x1 = 1e-5
    if abs(x2) < 1e-5:
        x2 = 1e-5
    if abs(z1) < 1e-5:
        z1 = 1e-5
    if abs(z2) < 1e-5:
        z2 = 1e-5

    tp1 = 6.2831853  # 2*pi
    dx = x2 - x1
    dz = z2 - z1

    # Magnetic field calculation (Shuey and Pasquale, 1973)
    if dx == 0.0 and dz == 0.0:
        return a, b

    dxiz = complex(dx, dz)
    f1 = (dxiz * (1.0 + vr1/y1)) / complex(x1, zmag1) + 1j/ysq * (x1*dz - zmag1*dx)
    f2 = (dxiz * (1.0 + vr2/y1)) / complex(x2, zmag2) + 1j/ysq * (x2*dz - zmag2*dx)
    fln = np.log(f2/f1) / dxiz

    q2 = dx * fln.real * qcf
    q1 = dz * fln.imag * qcf  # Note: there was a typo in original Fortran "eQCF"
    pz1 = -dx * fln.imag * pzcf
    px1 = dz * fln.real * pxcf
    b = q1 + pz1 + px1

    # Gravity field calculation (Cady, 1977)
    if abs(dx) < 0.0001:
        dx = 0.0001
    if abs(dz) < 0.0001:
        dz = 0.0001

    if nck > 0:
        return a, b

    em = dz / dx
    csq = 1.0 + em**2
    c = np.sqrt(dz*dz + dx*dx) / dx
    z0 = z1 - em * x1
    aa = z0 / c
    asq = aa * aa
    ak = z0 / csq
    x0 = em * ak
    bx = x2 + x0
    if abs(bx) < 0.0001:
        bx = 0.0001
    bi = x1 + x0
    if abs(bi) < 0.0001:
        bi = 0.0001

    cbx = c * bx
    cbi = c * bi
    jend = 1
    if abs(y1) < 0.001:
        jend = 0

    rsq1 = x1**2 + z1**2
    rsq2 = x2**2 + z2**2
    ry1 = np.sqrt(ysq + rsq1)
    ry11 = np.sqrt(ysq + rsq2)

    t1 = 0.0
    t2 = 0.0
    if rsq2 > 0.0:
        t1 = bx * np.log(rsq2)
    if rsq1 > 0.0:
        t2 = bi * np.log(rsq1)

    t3 = np.arctan2(bx, ak)
    if bx > 0.0 and ak < 0.0:
        t3 -= tp1

    t4 = np.arctan2(bi, ak)
    if bi > 0.0 and ak < 0.0:  # Note: original had "AJ" which seems to be a typo
        t4 -= tp1

    if jend == 0:
        a = -(t1 - t2 + 2.0*ak*(t3 - t4))
        return a, b

    # Additional terms for finite strike length
    t5 = bi * np.log((y1 + ry1)**2)
    t6 = bx * np.log((y1 + ry11)**2)
    t7 = y1/c * np.log((cbi + ry1)/(cbx + ry11))

    fnum = asq + ysq + y1 * ry11
    den = z0 * bx
    t9 = np.arctan2(fnum, den)
    if fnum < 0.0 and den < 0.0:
        t9 += tp1

    fnum = asq + ysq + y1 * ry1
    den = z0 * bi
    t11 = np.arctan2(fnum, den)
    if fnum < 0.0 and den < 0.0:
        t11 += tp1

    a = t1 - t2 + 2.0*ak*(t3 - t4) + t5 - t6 + t7*2.0 + ak*(t9*2.0 - t11*2.0)
    a = -a

    return a, b
import numpy as np


def execute_inversion(iterations, model, *args, **kwargs):
    print(f"This is where we would have a translation or wrapper of inver.f \
            {kwargs['ambient_field']}")

    nden = np.zeros((12,))
    nsus = np.zeros((12,))
    a1 = np.zeros((150, 50))
    ivz = np.zeros((12, 20))
    ivx = np.zeros((12, 20))
    gte = np.zeros((1, 32, 75))
    gdif = np.zeros((150,))
    mdif = np.zeros((150,))
    s = np.zeros((50,))
    v = np.zeros((50, 50))
    e = np.zeros((150,))
    w = np.zeros((150,))
    atw = np.zeros((150, 150, 4))
    _del = np.zeros((50,))

    im = iterations
    mpar = 0

    iiw = "I want to write to disk"

    # Set variables

    # INPUT THE ESTIMATED VARIANCE FOR GRAVITY, MAGNETICS
    vg = 0.0
    vm = 0.0

    mstat = model.nstat*2
    if(model.ian > 0):
        iden = 0
        isus = 0
        iver = 0
    else:
        # INPUT NO. OF DENSITY, SUSCEPTABLILITY, VERTEX \
        # PARAMETERS TO BE ADJUSTED
        iden = 0.0
        isus = 0.0
        iver = 0.0
    
    for i in range(0, model.npoly):
        nden[i] = 0
        nsus[i] = 0
        ns = model.nsides[i] + 1
        for j in range(0, ns):
            ivx[i, j] = 0
            ivz[i, j] = 0

    # INPUT PARAMETERS FOR INVERSION
    itest = 0
    if(iden <= 0):
        pass
    else:
        


    # Line 159 inver.f
    for i in range(0, model.nstat):
        k = stat*1
        for j in range(0, model.npoly):
            sgn = 1
            sgm = 1
            
            if(model.densty[j] < 0.0):
                sgn = -1.0
            if(model.suscp[j] < 0.0):
                sgm = -1.0
            
            nd = nden[j]
            ns = nsus[j]

            if(nd != 0):
                a1[i, nd] = a1[i, nd] + gte[j,i]*sgn
            if(ns != 0):
                a1[k, ns] = a1[k, ns] + mte[j, i]*sgm
            
            mtot[i] = mtot[i] + mte[j,i]*suscp[j]
            gtot[i] = gtot[i] + gte[j, i]*densty[j]*ct

            gtr = gtot[nbase] - grav[nbase]
            mtr = mtot[nbase] - mag[nbase]

            ssrm = 0.0
            ssr = 0.0

            for i in range(0, nstat):
                gtot[i] = gtot[i] - gtr
                gdif[i] = grav[i] - gtot[i]
                difsq = gdif[i]**2
                ssr = ssr + difsq
                ssrm = ssrm + difsq
                chisq = (ssr/vg)+(ssrm/vm)
    
    print(f"The new parameters are {iiw}")





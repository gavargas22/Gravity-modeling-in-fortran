# Gravity-modeling-in-fortran
Computer code written in about 1980 that needs to be updated


Build the fortran library:

`python -m numpy.f2py -c inver.f svd.f talw.f rotate.f -m inver`
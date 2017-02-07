#!/usr/bin/python

import numpy as np
import cmath

import pandas as pd
from pandas import Series, DataFrame

################################################################################
# setup of lookup tables for subduction coefficients. ##########################
################################################################################
# copy-pasted from Bastians rotation.nb file
# Subduction coefficients to irreps of octohedral group for all momenta

sqrt2 = np.sqrt(2.)
sqrt3 = np.sqrt(3.)
sqrt6 = np.sqrt(6.)

################################################################################
# T1
#T1 = [[[(np.asarray([0, 0, 0], dtype=int),),  1j/sqrt2, -1./sqrt2, 0]], \
#      [[(np.asarray([0, 0, 0], dtype=int),),  0,         0,        1j]], \
#      [[(np.asarray([0, 0, 0], dtype=int),), -1j/sqrt2, -1./sqrt2, 0]]]
#T1 = np.asarray(T1)

# TODO: Do I need p?
T1 = DataFrame({'p' : [(0,0,0)]*9, \
                '|J, M\rangle' : 
                            ["|1,+1\rangle", "|1, 0\rangle", "|1,-1\rangle"]*3, \
                'cg-coefficient' : [ 1, 0, 0, \
                                     0, 1, 0, \
                                     0, 0, 1 ]}, \
                index=pd.Index([1]*3+[2]*3+[3]*3, name='\mu'))

#T1 = DataFrame({'p' : [(0,0,0)]*9, \
#                '\gamma' : [(1,), (2,), (3,)]*3, \
#                'cg-coefficient' : [ 1j/sqrt2, -1./sqrt2, 0, \
#                                     0,         0,        1j, \
#                                    -1j/sqrt2, -1./sqrt2, 0]}, \
#                index=pd.Index([1]*3+[2]*3+[3]*3, name='\mu'))

#T1 = DataFrame({'p' : [np.array([0,0,0])]*9, \
#                '\gamma' : [(1,), (2,), (3,)]*3, 
#                'cg-coefficient' : [ 1j/sqrt2, -1./sqrt2, 0, \
#                                     0,         0,        1j, \
#                                    -1j/sqrt2, -1./sqrt2, 0]}, \
#                index=pd.Index([1]*3+[2]*3+[3]*3, name='\row'))

# In the CM-Frame this is equivalent to only taking the diagonal combinations
#T1 = [[[np.asarray([0, 0, 0], dtype=int), 1, 0, 0]], \
#      [[np.asarray([0, 0, 0], dtype=int), 0, 1, 0]], \
#      [[np.asarray([0, 0, 0], dtype=int), 0, 0, 1]]]
#T1 = np.asarray(T1)

################################################################################
# A1
A1 = [[[(np.asarray([ 0, 0, 1], dtype=int),),  0,         0,         1j], \
       [(np.asarray([ 0, 0,-1], dtype=int),),  0,         0,        -1j], \
       [(np.asarray([ 1, 0, 0], dtype=int),),  1j,        0,         0], \
       [(np.asarray([-1, 0, 0], dtype=int),), -1j,        0,         0], \
       [(np.asarray([ 0, 1, 0], dtype=int),),  0,         1j,        0], \
       [(np.asarray([ 0,-1, 0], dtype=int),),  0,        -1j,        0], \
       [(np.asarray([ 0, 1, 1], dtype=int),),  0,         1j/sqrt2,  1j/sqrt2], \
       [(np.asarray([ 0, 1,-1], dtype=int),),  0,         1j/sqrt2, -1j/sqrt2], \
       [(np.asarray([ 0,-1,-1], dtype=int),),  0,        -1j/sqrt2, -1j/sqrt2], \
       [(np.asarray([ 0,-1, 1], dtype=int),),  0,        -1j/sqrt2,  1j/sqrt2], \
       [(np.asarray([ 1, 0, 1], dtype=int),),  1j/sqrt2,  0,         1j/sqrt2], \
       [(np.asarray([ 1, 0,-1], dtype=int),),  1j/sqrt2,  0,        -1j/sqrt2], \
       [(np.asarray([-1, 0,-1], dtype=int),), -1j/sqrt2,  0,        -1j/sqrt2], \
       [(np.asarray([-1, 0, 1], dtype=int),), -1j/sqrt2,  0,         1j/sqrt2], \
       [(np.asarray([ 1, 1, 0], dtype=int),),  1j/sqrt2,  1j/sqrt2,  0], \
       [(np.asarray([-1, 1, 0], dtype=int),), -1j/sqrt2,  1j/sqrt2,  0], \
       [(np.asarray([-1,-1, 0], dtype=int),), -1j/sqrt2, -1j/sqrt2,  0], \
       [(np.asarray([ 1,-1, 0], dtype=int),),  1j/sqrt2, -1j/sqrt2,  0], \
       [(np.asarray([ 1, 1, 1], dtype=int),),  1j/sqrt3,  1j/sqrt3,  1j/sqrt3], \
       [(np.asarray([-1, 1, 1], dtype=int),), -1j/sqrt3,  1j/sqrt3,  1j/sqrt3], \
       [(np.asarray([-1,-1, 1], dtype=int),), -1j/sqrt3, -1j/sqrt3,  1j/sqrt3], \
       [(np.asarray([ 1,-1, 1], dtype=int),),  1j/sqrt3, -1j/sqrt3,  1j/sqrt3], \
       [(np.asarray([-1,-1,-1], dtype=int),), -1j/sqrt3, -1j/sqrt3, -1j/sqrt3], \
       [(np.asarray([ 1,-1,-1], dtype=int),),  1j/sqrt3, -1j/sqrt3, -1j/sqrt3], \
       [(np.asarray([ 1, 1,-1], dtype=int),),  1j/sqrt3,  1j/sqrt3, -1j/sqrt3], \
       [(np.asarray([-1, 1,-1], dtype=int),), -1j/sqrt3,  1j/sqrt3, -1j/sqrt3], \
       [(np.asarray([ 0, 0, 2], dtype=int),),  0,         0,         1j], \
       [(np.asarray([ 0, 0,-2], dtype=int),),  0,         0,        -1j], \
       [(np.asarray([ 2, 0, 0], dtype=int),), -1j,        0,         0], \
       [(np.asarray([-2, 0, 0], dtype=int),),  1j,        0,         0], \
       [(np.asarray([ 0, 2, 0], dtype=int),),  0,        -1j,        0], \
       [(np.asarray([ 0,-2, 0], dtype=int),),  0,         1j,        0]]]
A1 = np.asarray(A1)

################################################################################
# E2
E2 = [[[(np.asarray([ 0, 0, 1], dtype=int),),  0,       -1,       0], \
       [(np.asarray([ 0, 0,-1], dtype=int),),  0,       -1,       0], \
       [(np.asarray([ 1, 0, 0], dtype=int),),  0,       -1,       0], \
       [(np.asarray([-1, 0, 0], dtype=int),),  0,        1,       0], \
       [(np.asarray([ 0, 1, 0], dtype=int),),  1,        0,       0], \
       [(np.asarray([ 0,-1, 0], dtype=int),), -1,        0,       0], \
       [(np.asarray([ 1, 1, 1], dtype=int),),  1/sqrt2, -1/sqrt2, 0], \
       [(np.asarray([-1, 1, 1], dtype=int),),  1/sqrt2,  1/sqrt2, 0], \
       [(np.asarray([-1,-1, 1], dtype=int),), -1/sqrt2,  1/sqrt2, 0], \
       [(np.asarray([ 1,-1, 1], dtype=int),), -1/sqrt2, -1/sqrt2, 0], \
       [(np.asarray([-1,-1,-1], dtype=int),),  1/sqrt2, -1/sqrt2, 0], \
       [(np.asarray([ 1,-1,-1], dtype=int),),  1/sqrt2,  1/sqrt2, 0], \
       [(np.asarray([ 1, 1,-1], dtype=int),), -1/sqrt2,  1/sqrt2, 0], \
       [(np.asarray([-1, 1,-1], dtype=int),), -1/sqrt2, -1/sqrt2, 0], \
       [(np.asarray([ 0, 0, 2], dtype=int),),  0,       -1,       0], \
       [(np.asarray([ 0, 0,-2], dtype=int),),  0,       -1,       0], \
       [(np.asarray([ 2, 0, 0], dtype=int),),  0,       -1,       0], \
       [(np.asarray([-2, 0, 0], dtype=int),),  0,        1,       0], \
       [(np.asarray([ 0, 2, 0], dtype=int),),  1,        0,       0], \
       [(np.asarray([ 0,-2, 0], dtype=int),), -1,        0,       0]], \
                                                                    \
      [[(np.asarray([ 0, 0, 1], dtype=int),), -1j,        0,         0], \
       [(np.asarray([ 0, 0,-1], dtype=int),),  1j,        0,         0], \
       [(np.asarray([ 1, 0, 0], dtype=int),),  0,         0,         1j], \
       [(np.asarray([-1, 0, 0], dtype=int),),  0,         0,         1j], \
       [(np.asarray([ 0, 1, 0], dtype=int),),  0,         0,         1j], \
       [(np.asarray([ 0,-1, 0], dtype=int),),  0,         0,         1j], \
       [(np.asarray([ 1, 1, 1], dtype=int),), -1j/sqrt6, -1j/sqrt6,  2j/sqrt6], \
       [(np.asarray([-1, 1, 1], dtype=int),),  1j/sqrt6, -1j/sqrt6,  2j/sqrt6], \
       [(np.asarray([-1,-1, 1], dtype=int),),  1j/sqrt6,  1j/sqrt6,  2j/sqrt6], \
       [(np.asarray([ 1,-1, 1], dtype=int),), -1j/sqrt6,  1j/sqrt6,  2j/sqrt6], \
       [(np.asarray([-1,-1,-1], dtype=int),),  1j/sqrt6,  1j/sqrt6, -2j/sqrt6], \
       [(np.asarray([ 1,-1,-1], dtype=int),), -1j/sqrt6,  1j/sqrt6, -2j/sqrt6], \
       [(np.asarray([ 1, 1,-1], dtype=int),), -1j/sqrt6, -1j/sqrt6, -2j/sqrt6], \
       [(np.asarray([-1, 1,-1], dtype=int),),  1j/sqrt6, -1j/sqrt6, -2j/sqrt6], \
       [(np.asarray([ 0, 0, 2], dtype=int),), -1j,        0,         0], \
       [(np.asarray([ 0, 0,-2], dtype=int),),  1j,        0,         0], \
       [(np.asarray([ 2, 0, 0], dtype=int),),  0,         0,         1j], \
       [(np.asarray([-2, 0, 0], dtype=int),),  0,         0,         1j], \
       [(np.asarray([ 0, 2, 0], dtype=int),),  0,         0,         1j], \
       [(np.asarray([ 0,-2, 0], dtype=int),),  0,         0,         1j]]]
E2 = np.asarray(E2)

################################################################################
# B1
B1 = [[[(np.asarray([ 0, 1, 1], dtype=int),),  0,        -1/sqrt2,  1/sqrt2], \
       [(np.asarray([ 0, 1,-1], dtype=int),),  0,        -1/sqrt2, -1/sqrt2], \
       [(np.asarray([ 0,-1,-1], dtype=int),),  0,         1/sqrt2, -1/sqrt2], \
       [(np.asarray([ 0,-1, 1], dtype=int),),  0,         1/sqrt2,  1/sqrt2], \
       [(np.asarray([ 1, 0, 1], dtype=int),), -1/sqrt2,   0,        1/sqrt2], \
       [(np.asarray([ 1, 0,-1], dtype=int),),  1/sqrt2,   0,        1/sqrt2], \
       [(np.asarray([-1, 0,-1], dtype=int),), -1/sqrt2,   0,        1/sqrt2], \
       [(np.asarray([-1, 0, 1], dtype=int),),  1/sqrt2,   0,        1/sqrt2], \
       [(np.asarray([ 1, 1, 0], dtype=int),),  1/sqrt2,  -1/sqrt2, 0], \
       [(np.asarray([-1, 1, 0], dtype=int),), -1/sqrt2,  -1/sqrt2, 0], \
       [(np.asarray([-1,-1, 0], dtype=int),),  1/sqrt2,  -1/sqrt2, 0], \
       [(np.asarray([ 1,-1, 0], dtype=int),), -1/sqrt2,  -1/sqrt2, 0]]]

B1 = np.asarray(B1)

#################################################################################
# B2
B2 = [[[(np.asarray([ 0, 1, 1], dtype=int),), -1j,        0,        0], \
       [(np.asarray([ 0, 1,-1], dtype=int),),  1j,        0,        0], \
       [(np.asarray([ 0,-1,-1], dtype=int),), -1j,        0,        0], \
       [(np.asarray([ 0,-1, 1], dtype=int),),  1j,        0,        0], \
       [(np.asarray([ 1, 0, 1], dtype=int),),  0,        1j,        0], \
       [(np.asarray([ 1, 0,-1], dtype=int),),  0,        1j,        0], \
       [(np.asarray([-1, 0,-1], dtype=int),),  0,       -1j,        0], \
       [(np.asarray([-1, 0, 1], dtype=int),),  0,       -1j,        0], \
       [(np.asarray([ 1, 1, 0], dtype=int),),  0,        0,        1j], \
       [(np.asarray([-1, 1, 0], dtype=int),),  0,        0,       -1j], \
       [(np.asarray([-1,-1, 0], dtype=int),),  0,        0,       -1j], \
       [(np.asarray([ 1,-1, 0], dtype=int),),  0,        0,        1j]]]
B2 = np.asarray(B2)

################################################################################
def coefficients(irrep):
  if irrep is 'T1':
    return T1
  elif irrep is 'A1':
    return A1
  elif irrep is 'E2':
    return E2
  elif irrep is 'B1':
    return B1
  elif irrep is 'B2':
    return B2

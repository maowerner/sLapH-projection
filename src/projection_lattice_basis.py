import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import os

from asteval import Interpreter
aeval = Interpreter()
aeval.symtable['I'] = 1j

from ast import literal_eval

from utils import _scalar_mul, _abs2, _minus

def read_sc_2(p_cm_vecs, path, verbose=True, j=1):
  """
  Read subduction coefficients from SO(3) to irreducible representations of 
  appropriate little group of rotational symmetry for lattice in a reference 
  frame moving with momentum p_cm \in list_p_cm

  Parameters
  ----------
    p_cm_vecs : list
        Center of mass momentum of the lattice. Used to specify the appropriate
        little group of rotational symmetry. Contains integer 3-vectors
    path : string
        Path to files with subduction coefficients

  Returns
  -------
    df : pd.DataFrame
        Contains subduction coefficients for going from continuum to discete
        space. 
        Has columns Irrep, mult, J, M, coefficient, p, \mu and unnamed 
        indices

  Note
  ----
    Filename of subduction coefficients hardcoded. Expected to be 
    "J%d-P%1i%1i%1i-operators.txt"
  """

  subduction_coefficients = DataFrame()

  for p_cm_vec in p_cm_vecs:
    name = path +'/' + 'J{0}-P{1}-operators.txt'.format(\
           j, "".join([str(p) for p in eval(p_cm_vec)]))

    if not os.path.exists(name):
      print 'Warning: Could not find {}'.format(name)
      continue

    df = pd.read_csv(name, sep="\t", dtype=str)
    df.rename(columns=lambda x: x.strip(), inplace=True)

    df['p_{cm}'] = [p_cm_vec] * len(df)
    df.rename(columns={'alpha' : '\mu'}, inplace=True)
    del df['beta']
    df['mult'] = 1
    df = df.set_index(['p_{cm}', 'Irrep', '\mu', 'mult'])

    df['coefficient'] = df['coefficient'].apply(aeval)
    df['p^1'] = df['p^1'].apply(literal_eval).apply(str)
    df['p^2'] = df['p^2'].apply(literal_eval).apply(str)
    df['q'] = df['q'].apply(literal_eval).apply(str)
    df.rename(columns={'p^1' : 'p^{0}', 'p^2' : 'p^{1}'}, inplace=True)
    df = df[(df['p^{0}'] != str((0,0,0))) | (df['p^{1}'] != str((0,0,0)))]
    del df['abs(p1)']
    del df['abs(p2)']

    df['J^{0}'] = 0
    df['J^{1}'] = 0
    df['M^{0}'] = 0
    df['M^{1}'] = 0

    if verbose:
      print 'subduction_coefficients for {}'.format(p_cm_vec)
      print df, '\n'

    subduction_coefficients = pd.concat([subduction_coefficients, df])

  return subduction_coefficients.sort_index()


# TODO: Write a function to calculate cross product if basis is not 
#       complete and orthonormalize basis states
# To extend to 2 particle operators this must support use of 2 momenta as well.
# We get an additional column \vec{q} that works similar to the row of the 
# irrep. Either the maple script has to find unique operators, or an additional
# unique function must be used here. I prefer the former.
def read_sc(p_cm_vecs, path, verbose=True, j=1):
  """
  Read subduction coefficients from SO(3) to irreducible representations of 
  appropriate little group of rotational symmetry for lattice in a reference 
  frame moving with momentum p_cm \in list_p_cm

  Parameters
  ----------
    p_cm_vecs : list
        Center of mass momentum of the lattice. Used to specify the appropriate
        little group of rotational symmetry. Contains integer 3-vectors
    path : string
        Path to files with subduction coefficients

  Returns
  -------
    df : pd.DataFrame
        Contains subduction coefficients for going from continuum to discete
        space. 
        Has columns Irrep, mult, J, M, coefficient, p, \mu and unnamed 
        indices

  Note
  ----
    Filename of subduction coefficients hardcoded. Expected to be 
    "J%d-P%1i%1i%1i-operators.txt"
    # "lattice-basis_J%d_P%1i%1i%1i_Msum.dataframe"
  """

  subduction_coefficients = DataFrame()

  for p_cm_vec in p_cm_vecs:

#    name = path +'/' + 'lattice-basis_J{0}_P{1}_Msum.dataframe'.format(\
#           j, "".join([str(p) for p in eval(p_cm_vec)]))
    name = path +'/' + 'J{0}-P{1}-operators.txt'.format(\
           j, "".join([str(p) for p in eval(p_cm_vec)]))

    if not os.path.exists(name):
      print 'Warning: Could not find {}'.format(name)
      continue
    df = pd.read_csv(name, delim_whitespace=True, dtype=str) 

    df = pd.merge(df.ix[:,2:].stack().reset_index(level=1), df.ix[:,:2], 
                  left_index=True, 
                  right_index=True)

    # Munging of column names
    df.columns = ['M^{0}', 'coefficient', 'Irrep', '\mu']
    df['mult'] = 1
    df['p_{cm}'] = [p_cm_vec] * len(df)
    df['coefficient'] = df['coefficient'].apply(aeval)
    df['M^{0}'] = df['M^{0}'].apply(int)
    df = df.set_index(['p_{cm}', 'Irrep', '\mu', 'mult'])
    df['p^{0}'] = [p_cm_vec] * len(df)
    df['J^{0}'] = j
    df = df[['p^{0}','J^{0}','M^{0}','coefficient']]

    if verbose:
      print 'subduction_coefficients for {}'.format(p_cm_vec)
      print df, '\n'

    subduction_coefficients = pd.concat([subduction_coefficients, df])

  return subduction_coefficients.sort_index()



'''
Created on 2 Feb. 2015

compile with command line 
python setup.py build_ext --inplace

@author: francois belletti
'''

import numpy as np
cimport numpy as np
np.import_array()
cimport libc.stdlib
import ctypes

from datetime import datetime
from time import mktime

DTYPE = np.double
ctypedef np.double_t DTYPE_t
ITYPE = np.int32
ctypedef np.int32_t ITYPE_t

from libcpp.vector cimport vector
from libcpp.pair cimport pair
from libcpp.string cimport string
from libcpp.list cimport list
from libcpp cimport bool
from cython.operator cimport dereference as deref
                
cdef extern from "graph.h":
    cdef cppclass Graph[T1,T2]:
        # Reproduce signatures here
        Graph(const vector[pair[int, T1]] & node_features,
                const vector[vector[pair[int, T2]]] & neighbors)


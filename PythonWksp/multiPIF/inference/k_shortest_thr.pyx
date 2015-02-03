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
                
cdef extern from "exec.h":
    void get_k_shortest_threshold(int k_max,
                                  double threshold,
                                  int source_id,
                                  int sink_id,
                                  int * ids,
                                  double * lons,
                                  double * lats,
                                  int * neigh_origins,
                                  int * neigh_dests,
                                  double * neigh_weights,
                                  int n_vertices,
                                  int n_edges,
                                  vector[vector[int]] & path_results,
                                  vector[double] & path_costs)

def compute_k_shortest_threshold(k_max,
                                 threshold,
                                 source_id,
                                 sink_id,
                                 np.ndarray node_ids,
                                 np.ndarray node_lons,
                                 np.ndarray node_lats,
                                 np.ndarray neigh_origins,
                                 np.ndarray neigh_dests,
                                 np.ndarray neigh_weights):
    cdef vector[vector[int]]        path_results
    cdef vector[double]             path_costs
    cdef np.ndarray[ITYPE_t, ndim = 1, mode = 'c'] c_node_ids = \
        np.ascontiguousarray(node_ids, dtype = ITYPE)
    cdef np.ndarray[DTYPE_t, ndim = 1, mode = 'c'] c_node_lons = \
        np.ascontiguousarray(node_lons, dtype = DTYPE)
    cdef np.ndarray[DTYPE_t, ndim = 1, mode = 'c'] c_node_lats = \
        np.ascontiguousarray(node_lats, dtype = DTYPE)
    cdef np.ndarray[ITYPE_t, ndim = 1, mode = 'c'] c_neigh_origins = \
        np.ascontiguousarray(neigh_origins, dtype = ITYPE)
    cdef np.ndarray[ITYPE_t, ndim = 1, mode = 'c'] c_neigh_dests = \
        np.ascontiguousarray(neigh_dests, dtype = ITYPE)
    cdef np.ndarray[DTYPE_t, ndim = 1, mode = 'c'] c_neigh_weights = \
        np.ascontiguousarray(neigh_weights, dtype = DTYPE)
    get_k_shortest_threshold(k_max,
                             threshold,
                             source_id,
                             sink_id,
                             <int *>        c_node_ids.data,
                             <double *>     c_node_lons.data,
                             <double *>     c_node_lats.data,
                             <int *>        c_neigh_origins.data,
                             <int *>        c_neigh_dests.data,
                             <double *>     c_neigh_weights.data,
                             len(node_ids),
                             len(neigh_origins),
                             path_results,
                             path_costs)
    return {'paths' : path_results,
            'costs' : path_costs}
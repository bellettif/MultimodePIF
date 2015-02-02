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
		
cdef extern from "path.h":
	cdef cppclass Path[T]:
		Path[T]();
		
cdef extern from "graph.h":
	cdef cppclass Graph[T1,T2]:
		# Reproduce signatures here
		Graph(const vector[pair[int, T1]] & node_features,
          	  const vector[vector[pair[int, T2]]] & neighbors)
		
def estimate_likelihoods(np.ndarray A_proposal,
						 np.ndarray B_proposal,
						 terminals,
						 samples,
						 root_index):
	assert(A_proposal.shape[0] == A_proposal.shape[1] == A_proposal.shape[2] == B_proposal.shape[0])
	assert(B_proposal.shape[1] == len(terminals))
	N = A_proposal.shape[0]
	M = B_proposal.shape[1]
	n_samples = len(samples)
	cdef np.ndarray[DTYPE_t, ndim = 1, mode = 'c'] likelihoods = np.zeros(n_samples, dtype = DTYPE)
	cdef np.ndarray[DTYPE_t, ndim = 3, mode = 'c'] c_A_proposal = A_proposal
	cdef np.ndarray[DTYPE_t, ndim = 2, mode = 'c'] c_B_proposal = B_proposal
	cdef Flat_in_out* fio = new Flat_in_out(<double*> c_A_proposal.data,
											<double*> c_B_proposal.data,
	               							N, M,
	               		     				terminals,
	               		     				root_index)
	fio.compute_probas_flat(samples,
					   		<double*> likelihoods.data)
	del fio
	return likelihoods


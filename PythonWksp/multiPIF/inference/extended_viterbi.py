'''
Created on Feb 9, 2015
    
    Run the path inference Viterbi algorithm
    
@author: Francois Belletti
'''

import numpy as np


class Extended_Viterbi:
    
    pos_potials             = [] 
    path_potials            = []
    #
    pos_forward_potials     = []
    path_forward_potials    = []
    #
    pos_backward_potials    = []
    path_backward_potials   = []
    #
    pos_fwd_bwd_potials     = []
    path_fwd_bwd_potials    = []
    
    
    def __init__(self, pos_potentials, path_potentials):
        self.pos_potials     = pos_potentials
        self.path_potials    = path_potentials
        
    def compute_forward_potials(self):
        n_positions = len(self.pos_potials)
        self.pos_forward_potials.append(self.pos_potials[0])
        for i in xrange(n_positions - 1):
            prev_pos_pot        = self.pos_potials[i]
            current_path_pot    = self.path_potials[i]
            #    The following operation should be optimized with einsum
            current_path_fwd = np.dot(np.diag(prev_pos_pot), current_path_pot)
            self.pos_forward_potials.append(np.sum(current_path_fwd, axis = (0, 2)))
            self.path_forward_potials.append(np.copy(current_path_fwd))
    
    def compute_backward_potials(self):
        n_positions = len(self.pos_potials)
        self.pos_backward_potials.append(np.ones(len(self.pos_potials[-1]),
                                                 dtype = np.double))
        for i in xrange(n_positions - 1, 0, -1):
            next_pos_pot        = self.pos_potials[i]
            current_path_pot    = self.path_potials[i - 1]
            #    The following operation should be optimized with einsum
            current_path_bwd = np.dot(np.diag(next_pos_pot), 
                                      current_path_pot.transpose(1, 0, 2))
            self.pos_backward_potials.append(np.sum(current_path_bwd ,axis = (0, 2)))
            self.path_backward_potials.append(np.copy(current_path_bwd))
        self.pos_backward_potials.reverse()
        self.path_backward_potials.reverse()
            
    def compute_potials(self):
        n_positions = len(self.pos_potials)
        self.compute_forward_potials()
        self.compute_backward_potials()
        self.pos_fwd_bwd_potials.append(self.pos_forward_potials[0] * 
                                self.pos_backward_potials[-1])
        for i in xrange(n_positions - 1):
            self.pos_fwd_bwd_potials.append(self.pos_forward_potials[i] * 
                                            self.pos_backward_potials[-i])
            self.path_fwd_bwd_potials.append(self.path_forward_potials[i] *
                                             self.path_backward_potials[-i])
            
    def normalize_potials(self):
        n_positions = len(self.pos_potials)  
        self.pos_forward_potials[0]     /= np.sum(self.pos_forward_potials[0])
        self.pos_backward_potials[0]    /= np.sum(self.pos_backward_potials[0])
        self.pos_fwd_bwd_potials[0]     /= np.sum(self.pos_fwd_bwd_potials[0])
        for i in xrange(n_positions - 1):
            self.pos_forward_potials[i]     /= np.sum(self.pos_forward_potials[i])
            self.pos_backward_potials[i]    /= np.sum(self.pos_backward_potials[i])
            self.pos_fwd_bwd_potials[i]     /= np.sum(self.pos_fwd_bwd_potials[i])
            #
            self.path_forward_potials[i]    = np.apply_along_axis((lambda x : x / np.sum(x)), 
                                                                  2,
                                                                  self.path_forward_potials[i])
            self.path_backward_potials[i]   = np.apply_along_axis((lambda x : x / np.sum(x)), 
                                                                  2,
                                                                  self.path_backward_potials[i])
            self.path_fwd_bwd_potials[i]    = np.apply_along_axis((lambda x : x / np.sum(x)), 
                                                                  2,
                                                                  self.path_fwd_bwd_potials[i])
        
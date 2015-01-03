'''
Created on 8 mai 2014

@author: francois
'''

import numpy as np
from matplotlib import pyplot as plt

from Obs_generator import Obs_generator

class Markov_model:
    
    def __init__(self, initial, A, B, alphabet):
        self.initial = np.asarray(initial, dtype = np.double)
        self.initial /= np.sum(self.initial)
        self.A = np.asanyarray(A, dtype = np.double)
        sums = np.sum(self.A, axis = 1)
        for i, sum in enumerate(sums):
            self.A[i] /= sum
        self.generators = [Obs_generator(alphabet, weights) for weights in B]
        self.states = range(len(self.generators))
        self.current_state = np.random.choice(self.states, p = self.initial)
        
    def gen_obs(self):
        return self.generators[self.current_state].gen_obs()
    
    def transition(self):
        old_state = self.current_state
        self.current_state = np.random.choice(self.states, p = self.A[self.current_state])
        return self.current_state
            
    def generate_data(self, n_points):
        result = []
        for i in xrange(n_points):
            current_state = self.current_state
            obs = self.gen_obs()
            self.transition()
            result.append({'state' : current_state,
                           'obs' : obs})
        return result
        
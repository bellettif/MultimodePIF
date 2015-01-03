'''
Created on 8 mai 2014

@author: francois
'''

import numpy as np
from matplotlib import pyplot as plt

class Obs_generator:
    
    def __init__(self, alphabet, weights):
        self.alphabet = alphabet
        self.weights = np.asarray(weights, dtype = np.double)
        self.weights /= np.sum(self.weights)
        
    def gen_obs(self):
        return np.random.choice(self.alphabet, p = self.weights)

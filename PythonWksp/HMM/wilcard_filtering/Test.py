'''
Created on 8 mai 2014

@author: francois
'''

import numpy as np
from matplotlib import pyplot as plt

from surrogate.Markov_model import *
        
initial = [0.4, 0.8, 0.9]
A = [[0.1, 0.8, 0.1], [0.1, 0.1, 0.9], [0.9, 0.1 , 0.1]]
alphabet = [-1, -2, -3]
B = [[1.0, 0.5, 0.2], [0.2, 1.0, 0.5], [0.5, 0.2, 1.0]]
        
my_markov_model = Markov_model(initial, A, B, alphabet)


results = {}
for i in range(1000):
    current_state = my_markov_model.current_state
    if current_state not in results:
        results[current_state] = []
    results[current_state].append(my_markov_model.gen_obs())
    my_markov_model.transition()

for latent_state, current_obs in results.iteritems():
    plt.hist(current_obs)
    plt.title(latent_state)
    plt.show()
    

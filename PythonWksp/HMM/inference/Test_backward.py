'''
Created on 8 mai 2014

@author: francois
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
   
from surrogate.Markov_model import Markov_model
from HMM_algos import Proba_computer

initial = [0.1, 0.1, 0.1]
A = [[0.1, 0.5, 0.1], [0.1, 0.1, 0.5], [0.5, 0.1, 0.1]]
alphabet = ['a', 'b', 'c']
B = [[1.0, 0.5, 0.5], [0.5, 1.0, 0.5], [0.5, 0.5, 1.0]]

my_markov_model = Markov_model(initial,
                               A,
                               B,
                               alphabet)

data = my_markov_model.generate_data(10)
      
my_proba_computer = Proba_computer(initial,
                                 A,
                                 B,
                                 alphabet)

print [x['state'] for x in data]
print [x['obs'] for x in data]

backward_probas = my_proba_computer.compute_backward_probas([x['obs'] for x in data])

for i in xrange(backward_probas.shape[1]):
    print backward_probas[:,i]

plt.imshow(backward_probas, cmap = cm.gray)
plt.clim()
plt.show()
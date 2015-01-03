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
B = [[0.8, 0.1, 0.1], [0.1, 0.8, 0.1], [0.1, 0.1, 0.8]]

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

forwards = my_proba_computer.compute_forward_probas([x['obs'] for x in data])

plt.subplot(311)
plt.imshow(forwards, cmap = cm.gray)

backwards = my_proba_computer.compute_backward_probas([x['obs'] for x in data])

plt.subplot(312)
plt.imshow(backwards, cmap = cm.gray)

probas = my_proba_computer.compute_probas([x['obs'] for x in data])

for i in xrange(probas.shape[1]):
    print probas[:,i]

plt.subplot(313)
plt.imshow(probas, cmap = cm.gray)
plt.show()
plt.show()
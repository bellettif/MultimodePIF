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
A = [[0.3, 0.5, 0.3], [0.3, 0.3, 0.5], [0.5, 0.3, 0.3]]
alphabet = ['o', '*', 'p', 'h']
B = [[1.0, 0.5, 0.5, 0.5], [0.5, 1.0, 0.5, 0.5], [0.5, 0.5, 1.0, 0.5]]

my_markov_model = Markov_model(initial,
                               A,
                               B,
                               alphabet)

data = my_markov_model.generate_data(20)
      
my_proba_computer = Proba_computer(initial,
                                 A,
                                 B,
                                 alphabet)

states = np.asarray([x['state'] for x in data])
observations = [x['obs'] for x in data]

gammas = my_proba_computer.compute_probas(observations)

epsilons = my_proba_computer.compute_epsilons(observations)

print epsilons

gammas_eps = np.zeros((epsilons.shape[0], epsilons.shape[2]))

for t in xrange(gammas_eps.shape[1]):
    gammas_eps[:, t] = np.sum(epsilons[:, :, t], axis = 1)
    
print gammas_eps

print gammas


plt.subplot(411)
plt.imshow(gammas, cmap = cm.gray)
plt.clim()

deltas, psys, qs = my_proba_computer.viterbi(observations)

print deltas
print psys
print qs

plt.subplot(412)
plt.imshow(deltas, cmap = cm.gray)
plt.clim()

ymin = np.min(-qs)
ymax = np.max(-qs)

plt.subplot(413)
plt.plot(-qs, linestyle = '--', marker = 'o', markersize = 10)
plt.ylim((ymin - 1, ymax + 1))

plt.subplot(414)
for i, state in enumerate(states):
    plt.plot(i, -state, linestyle = 'None', markersize = 10, marker = observations[i], color = 'r')
plt.plot(-states, linestyle = '--', color = 'r')
plt.ylim((ymin - 1, ymax + 1))
plt.show()












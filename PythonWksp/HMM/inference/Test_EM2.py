'''
Created on 9 mai 2014

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

data = my_markov_model.generate_data(100)
      
proba_cpter = Proba_computer(initial,
                             A,
                             B,
                             alphabet)

states = np.asarray([x['state'] for x in data])
observations = [x['obs'] for x in data]

actual_initial = proba_cpter.initial
actual_A = proba_cpter.A
actual_B = proba_cpter.B

for i in xrange(100):
    initial = proba_cpter.initial
    A = proba_cpter.A
    B = proba_cpter.B
    new_initial, new_A, new_B = proba_cpter.estimate_new_model(observations)
    print 'Initial'
    print 'Model:'
    print initial
    print 'Estimated'
    print new_initial
    print '\n'
    print 'A'
    print 'Model:'
    print A
    print 'Estimated'
    print new_A
    print '\n'
    print 'Model:'
    print B
    print 'Estimated'
    print new_B
    proba_cpter.update_parameter(new_initial, new_A, new_B)

estimated_initial = new_initial
estimated_A = new_A
estimated_B = new_B

print '\n'
print 'Initial'
print 'Model:'
print actual_initial
print 'Estimated'
print estimated_initial
print '\n'
print 'A'
print 'Model:'
print actual_A
print 'Estimated'
print estimated_A
print '\n'
print 'Model:'
print actual_B
print 'Estimated'
print estimated_B


'''min_state = np.min(-states)
max_state = np.max(-states)

for i, state in enumerate(states):
    plt.plot(i, -state, linestyle = 'None', marker = observations[i], markersize = 10, color = 'r')
plt.ylim((min_state - 1, max_state + 1))
plt.plot(-states, linestyle = '--', color = 'r')
plt.show()

observations = [x['obs'] for x in data]'''
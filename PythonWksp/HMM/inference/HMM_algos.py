'''
Created on 8 mai 2014

@author: francois
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from surrogate.Markov_model import Markov_model

class Proba_computer:
    
    def __init__(self, initial, A, B, alphabet):
        self.initial = np.asarray(initial, dtype = np.double)
        self.initial /= np.sum(self.initial)
        self.A = np.asanyarray(A, dtype = np.double)
        sums = np.sum(self.A, axis = 1)
        for i, sum in enumerate(sums):
            self.A[i] /= sum
        self.B = np.asanyarray(B)
        sums = [np.sum(x) for x in self.B]
        for i, sum in enumerate(sums):
            self.B[i] /= sum
        self.alphabet = alphabet
        self.reversed_alphabet = {}
        for i, x in enumerate(alphabet):
            self.reversed_alphabet[x] = i
        self.n_states = len(self.initial)
        self.n_letters = len(self.alphabet)
            
    def compute_b(self, obs):
        return self.B[:,self.reversed_alphabet[obs]]
            
    def compute_forward_probas(self, data):
        alphas = np.zeros((self.n_states, len(data)))
        alphas[:,0] = self.initial * self.compute_b(data[0])
        alphas[:,0] /= np.sum(alphas[:,0])
        for t, datum in enumerate(data):
            if t == 0: continue
            alphas[:,t] = np.dot(alphas[:,t-1].T, self.A) * self.compute_b(datum)
            alphas[:,t] /= np.sum(alphas[:,t])
        return alphas
    
    def compute_backward_probas(self, data):
        alphas = np.zeros((self.n_states, len(data)))
        alphas[:,0] = self.initial * self.compute_b(data[0])
        alphas[:,0] /= np.sum(alphas[:,0])
        for t, datum in enumerate(data):
            if t == 0: continue
            alphas[:,t] = np.dot(alphas[:,t-1].T, self.A) * self.compute_b(datum)
            alphas[:,t] /= np.sum(alphas[:,t])
        betas = np.zeros((self.n_states, len(data)))
        betas[:,-1] = np.ones(self.n_states)
        betas[:,-1] /= np.sum(alphas[:,-1])
        for t, datum in enumerate(data[::-1]):
            if t == (len(data) - 1): break
            betas[:,-(t+2)] = np.dot(self.A, betas[:,-(t+1)] * self.compute_b(datum))
            betas[:,-(t+2)] /= np.sum(alphas[:,-(t+2)])
        return betas
    
    def compute_probas(self, data):
        gammas = self.compute_backward_probas(data) * self.compute_forward_probas(data)
        for i in xrange(gammas.shape[1]):
            gammas[:,i] /= np.sum(gammas[:,i])
        return gammas
        
    def viterbi(self, data):
        deltas = np.zeros((self.n_states, len(data)))
        psys = np.zeros((self.n_states, len(data)))
        deltas[:,0] = self.initial * self.compute_b(data[0])
        deltas[:,0] /= np.sum(deltas[:,0])
        psys[:,0] = np.zeros(self.n_states)
        for t, datum in enumerate(data):
            if t == 0: continue
            temp = np.dot(np.diag(deltas[:, t-1]), self.A)
            delta = np.max(temp, axis = 0) * self.compute_b(datum)
            deltas[:,t] = delta  
            deltas[:,t] /= np.sum(deltas[:,t])
            psys[:,t] = np.argmax(temp, axis = 0)
        qs = np.zeros(len(data))
        qs[-1] = np.argmax(deltas[:,-1])
        for t in xrange(len(data)):
            if t == (len(data) - 1): break
            qs[-(t+2)] = psys[qs[-(t+1)], -(t+1)]
        return deltas, psys, qs
        
    def compute_epsilons(self, data):
        alphas = self.compute_forward_probas(data)
        betas = self.compute_backward_probas(data)
        epsilons = np.zeros((self.n_states, self.n_states, len(data) - 1))
        for t in xrange(len(data) - 1):
            epsilons[:, :, t] = np.dot(np.diag(alphas[:,t]),
                                       np.dot(self.A,
                          np.diag(betas[:, t + 1] * self.compute_b(data[t + 1]))))
            epsilons[:, :, t] /= np.sum(epsilons[:, :, t])
        return epsilons
    
    def estimate_new_model(self, data):
        gammas = self.compute_probas(data)
        epsilons = self.compute_epsilons(data)
        new_initial = gammas[:,0]
        new_A = np.sum(epsilons, axis = 2)
        for i in range(self.n_states):
            new_A[i,:] /= np.sum(gammas[i,:-1])
        emission_mask = np.zeros((self.n_letters, len(data)))
        for t, datum in enumerate(data):
            emission_mask[self.reversed_alphabet[datum], t] = 1
        new_B = np.zeros((self.n_states, self.n_letters))
        for i in range(self.n_states):
            for j in range(self.n_letters):
                new_B[i, j] = np.sum(gammas[i,:] * emission_mask[j,:]) / np.sum(gammas[i,:])
        return new_initial, new_A, new_B
    
    def estimate_new_model_multi(self, list_of_datas):
        probas = [np.sum(self.compute_forward_probas(line)[:,-1]) for line in list_of_datas]
        models = [self.estimate_new_model(line) for line in list_of_datas]
        new_initials = np.zeros((self.n_states, len(models)))
        new_As = np.zeros((self.n_states, self.n_states, len(models)))
        new_Bs = np.zeros((self.n_states, self.n_letters, len(models)))
        for i in xrange(len(models)):
            new_initials[:,i] = models[i][0] * probas[i]
            new_As[:,:,i] = models[i][1] * probas[i]
            new_Bs[:,:,i] = models[i][2] * probas[i]
        new_initial = np.mean(new_initials, axis = 1)
        new_A = np.mean(new_As, axis = 2)
        new_B = np.mean(new_Bs, axis = 2)
        return new_initial, new_A, new_B
    
    def update_parameter(self, new_initial, new_A, new_B):
        self.initial = new_initial
        self.A = new_A
        self.B = new_B
        
        
        

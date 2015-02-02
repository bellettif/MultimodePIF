'''
Created on 20 mai 2014

@author: francois
'''

import SCFG_c
from SCFG_c import Looping_der_except

from internal_grammar_distance import compute_distance_matrix

import numpy as np
from matplotlib import pyplot as plt

import os
import shutil
import string
import itertools
import pydot

import time

def normalize_slices(A, B):
    assert(A.ndim == 3)
    assert(B.ndim == 2)
    assert(A.shape[0] == A.shape[1] == A.shape[2] == B.shape[0])
    for i in xrange(A.shape[0]):
        total = np.sum(A[i,:,:]) + np.sum(B[i,:])
        A[i,:,:] /= total
        B[i,:] /= total
    return A, B

def merge_rules(A, B,
                first_index,
                second_index):
    if first_index > second_index:
        temp = first_index
        first_index = second_index
        second_index = temp
    assert(A.ndim == 3)
    assert(B.ndim == 2)
    assert(A.shape[0] == A.shape[1] == A.shape[2] == B.shape[0])
    assert(first_index in range(A.shape[0]))
    assert(second_index in range(A.shape[0]))
    assert(first_index != second_index)
    sub_selection = range(A.shape[0])
    sub_selection = filter(lambda x : x != second_index, sub_selection)
    new_A = np.copy(A)
    old_A = A
    new_A[first_index, :, :] = 0.5 * old_A[first_index, :, :] + 0.5 * old_A[second_index, :, :]
    new_A[:, first_index, :] += old_A[:, second_index, :]
    new_A[:, :, first_index] += old_A[:, :, second_index]
    new_A = new_A[np.ix_(sub_selection, sub_selection, sub_selection)]
    old_B = np.copy(B)
    new_B = old_B[sub_selection]
    new_B[first_index] = 0.5 * old_B[first_index] + 0.5 * old_B[second_index]
    return new_A, new_B

def expand_rule(A, B,
                target_index):
    assert(A.ndim == 3)
    assert(B.ndim == 2)
    assert(A.shape[0] == A.shape[1] == A.shape[2] == B.shape[0])
    assert(target_index in range(A.shape[0]))
    new_index = target_index + 1
    sub_selection = range(A.shape[0] + 1)
    sub_selection = filter(lambda x : x != new_index, sub_selection)
    new_A = np.zeros((A.shape[0] + 1, A.shape[0] + 1, A.shape[0] + 1))
    new_A[np.ix_(sub_selection, sub_selection, sub_selection)] = A
    for i in sub_selection:
        new_A[np.ix_([i], [target_index], sub_selection)] *= 0.5
        if i <= target_index:
            new_A[np.ix_([i], [new_index], sub_selection)] = A[i, target_index, :]
        else:
            new_A[np.ix_([i], [new_index], sub_selection)] = A[i - 1, target_index, :]
        new_A[np.ix_([i], [new_index], sub_selection)] *= 0.5
        new_A[np.ix_([i], sub_selection, [target_index])] *= 0.5
        if i <= target_index:
            new_A[np.ix_([i], sub_selection, [new_index])] = A[np.ix_([i], range(A.shape[2]), [target_index])]
        else:
            new_A[np.ix_([i], sub_selection, [new_index])] = A[np.ix_([i - 1], range(A.shape[2]), [target_index])]
        new_A[np.ix_([i], sub_selection, [new_index])] *= 0.5
        if i <= target_index:
            new_A[i,target_index, target_index] = A[i,target_index,target_index] * 0.25
            new_A[i,target_index, new_index] = new_A[i,target_index, target_index]
            new_A[i,new_index, target_index] = new_A[i,target_index, target_index]
            new_A[i,new_index, new_index] = new_A[i,target_index, target_index]
        else:
            new_A[i,target_index, target_index] = A[i-1,target_index,target_index] * 0.25
            new_A[i,target_index, new_index] = new_A[i,target_index, target_index]
            new_A[i,new_index, target_index] = new_A[i,target_index, target_index]
            new_A[i,new_index, new_index] = new_A[i,target_index, target_index]
    new_A[new_index] = new_A[target_index]
    new_B = np.zeros((B.shape[0] + 1, B.shape[1]))
    new_B[sub_selection] = B
    new_B[new_index] = new_B[target_index]
    return new_A, new_B
    
def compute_KL_signature(first_sign, second_sign):
    if set(first_sign.keys()) != set(second_sign.keys()):
        return np.inf
    else:
        result = 0
        for key in first_sign.keys():
            p = first_sign[key]
            q = second_sign[key]
            result += p * np.log(p / q) + q * np.log(q / p)
        return result

class SCFG:
    
    def __init__(self, root_index = 0):
        self.term_chars = []
        self.term_char_to_index = {}
        self.A = np.zeros((0, 0, 0), dtype = np.double)
        self.B = np.zeros((0, 0), dtype = np.double)
        self.N = 0
        self.M = 0
        #
        self.rules_mapped = False
        self.rules = {}
        #
        self.root_index = root_index
        #
        self.internal_distances = np.zeros((0, 0))
        self.ranked_internal_distances = []
        
    # Rule_dict[int] = (list of int pairs, list of weights, list of terms, list_of_weights)
    def init_from_rule_dict(self, rule_dict):
        self.N = len(rule_dict)
        assert sorted(rule_dict.keys()) == range(self.N)
        #
        #    Grabbing all terminal characters
        #
        all_terms = []
        for list_of_pairs, list_of_weights, list_of_terms, list_of_term_weights in rule_dict.values():
            all_terms.extend(list_of_terms)
            for left, right in list_of_pairs:
                assert(left in rule_dict)
                assert(right in rule_dict)
        self.term_chars = sorted(list(set(all_terms)))
        assert(len(self.term_chars) > 0)
        self.M = len(self.term_chars)
        for i, term_char in enumerate(self.term_chars):
            self.term_char_to_index[term_char] = i
        #
        #    Building A and B matrices
        #
        self.A = np.zeros((self.N, self.N, self.N), dtype = np.double)
        self.B = np.zeros((self.N, self.M), dtype = np.double)
        for i in xrange(self.N):
            list_of_pairs, list_of_weights, list_of_terms, list_of_term_weights = rule_dict[i]
            assert(len(list_of_pairs) == len(list_of_weights))
            assert(len(list_of_terms) == len(list_of_term_weights))
            for l in xrange(len(list_of_pairs)):
                left, right = list_of_pairs[l]
                weight = list_of_weights[l]
                self.A[i, left, right] = weight
            for l in xrange(len(list_of_terms)):
                term = list_of_terms[l]
                weight = list_of_term_weights[l]
                self.B[i, self.term_char_to_index[term]] = weight     
        normalize_slices(self.A, self.B)          
        
    def init_from_A_B(self, A, B, term_chars):
        assert(len(term_chars) > 0)
        assert(A.ndim == 3)
        assert(B.ndim == 2)
        assert(A.shape[0] == A.shape[1] == A.shape[2] == B.shape[0])
        assert(B.shape[1] == len(term_chars))
        self.N = A.shape[0]
        self.M = B.shape[1]
        self.A = np.copy(A)
        self.B = np.copy(B)
        normalize_slices(self.A, self.B)
        self.term_chars = term_chars
        for i, term in enumerate(self.term_chars):
            self.term_char_to_index[term] = i
      
    def rotate(self, new_root_index):
        self.root_index = new_root_index
            
    def map_rules(self):
        self.rules = {}
        for i in xrange(self.A.shape[0]):
            derivation_indices = itertools.product(range(self.A.shape[0]),
                                                   range(self.A.shape[0]))
            A_items = zip(derivation_indices, np.ravel(self.A[i]))
            A_items = filter(lambda x : x[1] != 0, A_items)
            B_items = zip(range(self.B.shape[1]), self.B[i])
            B_items = filter(lambda x : x[1] != 0, B_items)
            pairs = [x[0] for x in A_items]
            pair_weights = [x[1] for x in A_items]
            terms = [self.term_chars[x[0]] for x in B_items]
            term_weights = [x[1] for x in B_items]
            self.rules[i] = (pairs, pair_weights, terms, term_weights)
        self.rules_mapped = True
        
    def print_rules(self):
        if not self.rules_mapped:
            self.map_rules()
        print 'Root_rule %d:' % self.root_index
        rule = self.rules[self.root_index]
        print '\tPairs:'
        print zip(rule[0], rule[1])
        print '\tTerms:'
        print zip(rule[2], rule[3])
        print ''
        for i, rule in self.rules.iteritems():
            if i == self.root_index: continue
            print 'Rule %d:' % i
            print '\tPairs:'
            print zip(rule[0], rule[1])
            print '\tTerms:'
            print zip(rule[2], rule[3])
            print ''
            
    def merge(self, first_index, second_index):
        self.A, self.B = merge_rules(self.A, 
                    self.B,
                    first_index,
                    second_index)
        self.N = self.A.shape[0]
        self.rules_mapped = False
        self.rules = {}
        #
        self.internal_distances = np.zeros((0, 0))
        self.ranked_internal_distances = []
        
        
    def expand(self, target_index):
        self.A, self.B = expand_rule(self.A,
                    self.B,
                    target_index)
        self.N = self.A.shape[0]
        self.rules_mapped = False
        self.rules = {}
            
    def produce_sentences(self, n_sentences, max_length = 0):
        if max_length == 0:
            return SCFG_c.produce_sentences(self.A,
                                            self.B,
                                            self.term_chars,
                                            n_sentences,
                                            self.root_index)
        else:
            return filter(lambda x : len(x) < max_length,
                          SCFG_c.produce_sentences(self.A,
                                            self.B,
                                            self.term_chars,
                                            n_sentences,
                                            self.root_index))
            
    def estimate_likelihoods(self,
                             samples,
                             A_proposal = 0,
                             B_proposal = 0,
                             term_chars = []):
        assert(len(samples) > 0)
        if(A_proposal == 0 or B_proposal == 0 or len(term_chars) == 0):
            assert(A_proposal == 0 and B_proposal == 0 and len(term_chars) == 0)
            return SCFG_c.estimate_likelihoods(self.A,
                                               self.B,
                                               self.term_chars,
                                               samples,
                                               self.root_index)
        else:
            assert(A_proposal.ndim == 3)
            assert(B_proposal.ndim == 2)
            assert(A_proposal.shape[0] == A_proposal.shape[1] == A_proposal.shape[2] == B_proposal.shape[0])
            assert(B_proposal.shape[1] == len(term_chars))
            return SCFG_c.estimate_likelihoods(A_proposal,
                                               B_proposal,
                                               term_chars,
                                               samples,
                                               self.root_index)
            
    #
    #    Option in  ['all', 'keep_zeros', 'keep_zeros_A', 'keep_zeros_B']
    #
    def blur_A_B(self,
                 option = 'all',
                 noise_source_A = 0,
                 param_1_A = 0,
                 param_2_A = 0,
                 epsilon_A = 0,
                 noise_source_B = 0,
                 param_1_B = 0,
                 param_2_B = 0,
                 epsilon_B = 0):
        assert(option in ['all', 'keep_zeros',
                          'keep_zeros_A', 'keep_zeros_B'])
        if option == 'all':
            if noise_source_A != 0:
                self.A += noise_source_A(param_1_A, param_2_A, (self.N, self.N, self.N))
                self.A = np.maximum(self.A, epsilon_A * np.ones((self.N, self.N, self.N)))
            if noise_source_B != 0:
                self.B += noise_source_B(param_1_B, param_2_B, (self.N, self.M))
                self.B = np.maximum(self.B, epsilon_B * np.ones((self.N, self.M)))
            normalize_slices(self.A, self.B)          
        if option == 'keep_zeros':
            A_zeros = np.where(self.A == 0)
            B_zeros = np.where(self.B == 0)
            if noise_source_A != 0:
                self.A += noise_source_A(param_1_A, param_2_A, (self.N, self.N, self.N))
                self.A = np.maximum(self.A, epsilon_A * np.ones((self.N, self.N, self.N)))
            if noise_source_B != 0:
                self.B += noise_source_B(param_1_B, param_2_B, (self.N, self.M))
                self.B = np.maximum(self.B, epsilon_B * np.ones((self.N, self.M)))
            self.A[A_zeros] = 0
            self.B[B_zeros] = 0
            normalize_slices(self.A, self.B)
        if option == 'keep_zeros_A':
            A_zeros = np.where(self.A == 0)
            if noise_source_A != 0:
                self.A += noise_source_A(param_1_A, param_2_A, (self.N, self.N, self.N))
                self.A = np.maximum(self.A, epsilon_A * np.ones((self.N, self.N, self.N)))
            if noise_source_B != 0:
                self.B += noise_source_B(param_1_B, param_2_B, (self.N, self.M))
                self.B = np.maximum(self.B, epsilon_B * np.ones((self.N, self.M)))
            self.A[A_zeros] = 0
            normalize_slices(self.A, self.B)
        if option == 'keep_zeros_B':
            B_zeros = np.where(self.B == 0)
            if noise_source_A != 0:
                self.A += noise_source_A(param_1_A, param_2_A, (self.N, self.N, self.N))
                self.A = np.maximum(self.A, epsilon_A * np.ones((self.N, self.N, self.N)))
            if noise_source_B != 0:
                self.B += noise_source_B(param_1_B, param_2_B, (self.N, self.M))
                self.B = np.maximum(self.B, epsilon_B * np.ones((self.N, self.M)))
            self.B[B_zeros] = 0
            normalize_slices(self.A, self.B)
            
    #    
    #    Init option = exact, perturbated (need to give perturbation options),
    #            perturbated_keep_zeros, explicit
    #    Returns c_new_A, c_new_B, likelihoods
    #
    def estimate_A_B(self,
                     samples,
                     n_iterations,
                     init_option = 'exact',
                     A_proposal = 0,
                     B_proposal = 0,
                     term_chars = [],
                     noise_source_A = 0,
                     param_1_A = 0,
                     param_2_A = 0,
                     epsilon_A = 0,
                     noise_source_B = 0,
                     param_1_B = 0,
                     param_2_B = 0,
                     epsilon_B = 0):
        assert(init_option in ['exact',
                               'perturbated',
                               'perturbated_keep_zeros',
                               'explicit',
                               'explicit_keep_zeros',
                               'random'])
        assert(n_iterations > 0)
        assert(len(samples) > 0)
        if init_option == 'exact':
            return SCFG_c.iterate_estimation(self.A,
                                             self.B,
                                             self.term_chars,
                                             samples,
                                             n_iterations,
                                             self.root_index)
        if init_option == 'perturbated':
            assert(A_proposal == 0 and B_proposal == 0 and len(term_chars) == 0)
            A_proposal = self.A + noise_source_A(param_1_A, param_2_A, (self.N, self.N, self.N))
            A_proposal = np.maximum(A_proposal, epsilon_A * np.ones((self.N, self.N, self.N)))
            B_proposal = self.B + noise_source_B(param_1_B, param_2_B, (self.N, self.M))
            B_proposal = np.maximum(B_proposal, epsilon_B * np.ones((self.N, self.M)))
            normalize_slices(A_proposal, B_proposal)
            return SCFG_c.iterate_estimation(A_proposal,
                                             B_proposal,
                                             self.term_chars,
                                             samples,
                                             n_iterations,
                                             self.root_index)
        if init_option == 'perturbated_keep_zeros':
            assert(A_proposal == 0 and B_proposal == 0 and len(term_chars) == 0)
            A_proposal = self.A + noise_source_A(param_1_A, param_2_A, (self.N, self.N, self.N))
            A_proposal = np.maximum(A_proposal, epsilon_A * np.ones((self.N, self.N, self.N)))
            B_proposal = self.B + noise_source_B(param_1_B, param_2_B, (self.N, self.M))
            B_proposal = np.maximum(B_proposal, epsilon_B * np.ones((self.N, self.M)))
            A_proposal[np.where(self.A == 0)] = 0
            B_proposal[np.where(self.B == 0)] = 0
            normalize_slices(A_proposal, B_proposal)
            return SCFG_c.iterate_estimation(A_proposal,
                                             B_proposal,
                                             self.term_chars,
                                             samples,
                                             n_iterations,
                                             self.root_index)
        if init_option == 'explicit':
            assert(noise_source_A == 0 and
                   param_1_A == 0 and
                   param_2_A == 0 and
                   epsilon_A == 0 and
                   noise_source_B == 0 and
                   param_1_B == 0 and
                   param_2_B == 0 and
                   epsilon_B == 0)
            if len(term_chars) == 0:
                term_chars = self.term_chars
            assert(A_proposal.ndim == 3)
            assert(B_proposal.ndim == 2)
            assert(A_proposal.shape[0] == A_proposal.shape[1] == A_proposal.shape[2] == B_proposal.shape[0])
            assert(B_proposal.shape[1] == len(term_chars))
            normalize_slices(A_proposal, B_proposal)
            return SCFG_c.iterate_estimation(A_proposal,
                                             B_proposal,
                                             term_chars,
                                             samples,
                                             n_iterations,
                                             self.root_index)
        if init_option == 'explicit_keep_zeros':
            assert(noise_source_A == 0 and
                   param_1_A == 0 and
                   param_2_A == 0 and
                   epsilon_A == 0 and
                   noise_source_B == 0 and
                   param_1_B == 0 and
                   param_2_B == 0 and
                   epsilon_B == 0)
            if len(term_chars) == 0:
                term_chars = self.term_chars
            assert(A_proposal.ndim == 3)
            assert(B_proposal.ndim == 2)
            assert(A_proposal.shape[0] == A_proposal.shape[1] == A_proposal.shape[2] == B_proposal.shape[0])
            assert(B_proposal.shape[1] == len(term_chars))
            A_proposal[np.where(self.A == 0)] = 0
            B_proposal[np.where(self.B == 0)] = 0
            normalize_slices(A_proposal, B_proposal)
            return SCFG_c.iterate_estimation(A_proposal,
                                             B_proposal,
                                             term_chars,
                                             samples,
                                             n_iterations,
                                             self.root_index)
        if init_option == 'random':
            assert(A_proposal.ndim != 0)
            assert(B_proposal.ndim != 0)
            assert(noise_source_A == 0)
            assert(param_1_A != 0)
            assert(param_2_A != 0)
            assert(epsilon_A == 0)
            assert(noise_source_B == 0)
            assert(param_1_B != 0)
            assert(param_2_B == 0)
            assert(epsilon_B == 0)
            if len(term_chars) == 0:
                term_chars = self.term_chars
            assert(A_proposal.ndim == 3)
            assert(B_proposal.ndim == 2)
            assert(A_proposal.shape[0] == A_proposal.shape[1] == A_proposal.shape[2] == B_proposal.shape[0])
            assert(B_proposal.shape[1] == len(term_chars))
            N = A_proposal.shape[0]
            M = len(term_chars)
            n_D = N - M
            alpha_1_D = param_1_A
            alpha_2_D = param_2_A
            alpha_T = param_1_B
            for i in xrange(n_D):
                beta = np.random.dirichlet(alpha_1_D * 
                           np.ones(N, np.double))
                beta_beta = np.outer(beta, beta)
                weights = np.random.dirichlet(alpha_2_D * 
                          np.ones(N ** 2, np.double))
                A_proposal[i, :, :] = np.reshape(weights, (N, N)) * beta_beta
            for i in xrange(n_D, N):
                B_proposal[i, :] = np.random.dirichlet(alpha_T * 
                                       np.ones(M, dtype = np.double))
            normalize_slices(A_proposal, B_proposal)
            A_proposal = np.asanyarray(A_proposal, 
                                       dtype = np.double)
            B_proposal = np.asanyarray(B_proposal,
                                       dtype = np.double)
            return SCFG_c.iterate_estimation(A_proposal,
                                             B_proposal,
                                             term_chars,
                                             samples,
                                             n_iterations,
                                             self.root_index)
            
            
    def plot_grammar_matrices(self,
                              folder_path,
                              folder_name,
                              A_matrix = np.zeros(0),
                              B_matrix = np.zeros(0)):
        if folder_name in os.listdir(folder_path):
            shutil.rmtree(folder_path + '/' + folder_name,
                          True)
        os.mkdir(folder_path + '/' + folder_name)
        if(len(A_matrix) == 0):
            A_matrix = self.A
        if(len(B_matrix) == 0):
            B_matrix = self.B
        assert(A_matrix.shape[0] == A_matrix.shape[1] == A_matrix.shape[2] == B_matrix.shape[0])
        N = A_matrix.shape[0]
        for i in xrange(N):
            plt.subplot(211)
            plt.title('A %d' % i)
            plt.imshow(A_matrix[i], interpolation = 'None')
            plt.clim(0, 1.0)
            plt.subplot(212)
            plt.plot(range(len(B_matrix[i])), B_matrix[i], linestyle = 'None', marker = 'o')
            plt.ylim(-0.2, 1.0)
            plt.xlim(-1, len(B_matrix[i]))
            plt.title('B %d' % i)
            plt.savefig(folder_path + '/' + folder_name + '/' + string.lower(folder_name) + '_rule_' + str(i) + '.png', dpi = 300)
            plt.close()
        
    def compare_grammar_matrices_3(self,
                                 folder_path,
                                 folder_name,
                                 A_1_matrix = np.zeros(0),
                                 B_1_matrix = np.zeros(0),
                                 A_2_matrix = np.zeros(0),
                                 B_2_matrix = np.zeros(0),
                                 A_3_matrix = np.zeros(0),
                                 B_3_matrix = np.zeros(0)):
        if folder_name in os.listdir(folder_path):
            shutil.rmtree(folder_path + '/' + folder_name,
                          True)
        os.mkdir(folder_path + '/' + folder_name)
        if(len(A_3_matrix) == 0):
            A_3_matrix = self.A
        if(len(B_3_matrix) == 0):
            B_3_matrix = self.B
        assert(A_1_matrix.shape[0] == A_1_matrix.shape[1] == A_1_matrix.shape[2] == B_1_matrix.shape[0])
        assert(A_2_matrix.shape[0] == A_2_matrix.shape[1] == A_2_matrix.shape[2] == B_2_matrix.shape[0])
        assert(A_3_matrix.shape[0] == A_3_matrix.shape[1] == A_3_matrix.shape[2] == B_3_matrix.shape[0])
        N = A_1_matrix.shape[0]
        for i in xrange(N):
            plt.subplot(231)
            plt.title('First A matrix %d' % i)
            plt.imshow(A_1_matrix[i])
            plt.clim(0, 1.0)
            plt.subplot(232)
            plt.title('Second A matrix %d' % i)
            plt.imshow(A_2_matrix[i])
            plt.clim(0, 1.0)
            plt.subplot(233)
            plt.title('Third A matrix %d' % i)
            plt.imshow(A_3_matrix[i])
            plt.clim(0, 1.0)
            plt.subplot(234)
            plt.plot(range(len(B_1_matrix[i])), B_1_matrix[i], linestyle = 'None', marker = 'o')
            plt.ylim(-0.2, 1.0)
            plt.xlim(-1, len(B_1_matrix[i]))
            plt.title('First B matrix %d' % i)
            plt.subplot(235)          
            plt.plot(range(len(B_2_matrix[i])), B_2_matrix[i], linestyle = 'None', marker = 'o')
            plt.ylim(-0.2, 1.0)
            plt.xlim(-1, len(B_2_matrix[i]))
            plt.title('Second B matrix %d' % i)
            plt.subplot(236)          
            plt.plot(range(len(B_3_matrix[i])), B_3_matrix[i], linestyle = 'None', marker = 'o')
            plt.ylim(-0.2, 1.0)
            plt.xlim(-1, len(B_3_matrix[i]))
            plt.title('Third B matrix %d' % i)
            plt.savefig(folder_path + '/' + folder_name + '/' + string.lower(folder_name) + '_compare_rule_' + str(i) + '.png', dpi = 300)
            plt.close()
            
    def compare_grammar_matrices(self,
                                 folder_path,
                                 folder_name,
                                 A_1_matrix = np.zeros(0),
                                 B_1_matrix = np.zeros(0),
                                 A_2_matrix = np.zeros(0),
                                 B_2_matrix = np.zeros(0)):
        if folder_name in os.listdir(folder_path):
            shutil.rmtree(folder_path + '/' + folder_name,
                          True)
        os.mkdir(folder_path + '/' + folder_name)
        if(len(A_2_matrix) == 0):
            A_2_matrix = self.A
        if(len(B_2_matrix) == 0):
            B_2_matrix = self.B
        assert(A_1_matrix.shape[0] == A_1_matrix.shape[1] == A_1_matrix.shape[2] == B_1_matrix.shape[0])
        assert(A_2_matrix.shape[0] == A_2_matrix.shape[1] == A_2_matrix.shape[2] == B_2_matrix.shape[0])
        N = A_1_matrix.shape[0]
        for i in xrange(N):
            plt.subplot(221)
            plt.title('First A matrix %d' % i)
            plt.imshow(A_1_matrix[i])
            plt.clim(0, 1.0)
            plt.subplot(222)
            plt.title('Second A matrix %d' % i)
            plt.imshow(A_2_matrix[i])
            plt.clim(0, 1.0)  
            plt.subplot(223)          
            plt.plot(range(len(B_1_matrix[i])), B_1_matrix[i], linestyle = 'None', marker = 'o')
            plt.ylim(-0.2, 1.0)
            plt.xlim(-1, len(B_1_matrix[i]))
            plt.title('First B matrix %d' % i)
            plt.subplot(224)          
            plt.plot(range(len(B_2_matrix[i])), B_2_matrix[i], linestyle = 'None', marker = 'o')
            plt.ylim(-0.2, 1.0)
            plt.xlim(-1, len(B_2_matrix[i]))
            plt.title('Second B matrix %d' % i)
            plt.savefig(folder_path + '/' + folder_name + '/' + string.lower(folder_name) + '_compare_rule_' + str(i) + '.png', dpi = 300)
            plt.close()
            
    def plot_stats(self, n_samples, max_length = 0, 
                   max_represented = 0,
                   filename = ''):
        first_time = time.clock()
        freqs, strings = SCFG_c.compute_stats(self.A,
                                              self.B,
                                              self.term_chars,
                                              n_samples,
                                              max_length,
                                              self.root_index)
        print time.clock() - first_time
        freqs = np.asarray(freqs, dtype = np.double)
        total = float(np.sum(freqs))
        print 'Number of sentences %f' % total
        freqs /= total
        entropy = -np.sum(freqs * np.log(freqs))
        indices = range(len(freqs))
        indices.sort(key = (lambda i : -freqs[i]))
        freqs = [freqs[i] for i in indices]
        strings = [strings[i] for i in indices]
        if max_represented != 0:
            freqs = freqs[:max_represented]
            strings = strings[:max_represented]
        plt.bar(np.arange(len(strings)), np.log(freqs), align = 'center')
        plt.xticks(np.arange(len(strings)), strings, rotation = 'vertical', fontsize = 4)
        plt.title('Frequences (%d sequences, %f entropy)' % (int(total), entropy))
        if filename == '':
            plt.show()
        else:
            plt.savefig(filename, dpi = 300)
            plt.close()
            
    def compute_signature(self, n_samples, epsilon = 0, max_length = 0):
        freqs, strings = SCFG_c.compute_stats(self.A,
                                              self.B,
                                              self.term_chars,
                                              n_samples,
                                              max_length = 0,
                                              root_index = self.root_index)
        freqs = np.asarray(freqs, dtype = np.double)
        total = float(np.sum(freqs))
        freqs /= total
        if max_length == 0 and epsilon != 0:
            indices = range(len(freqs))
            indices.sort(key = (lambda i : -freqs[i]))
            freqs = [freqs[i] for i in indices]
            strings = [strings[i].split(' ') for i in indices]
            length_weight = {}
            all_lengths = set([len(x) for x in strings])
            for length in all_lengths:
                good_indices = filter(lambda i : len(strings[i]) == length, range(len(strings)))
                length_weight[length] = sum([freqs[i] for i in good_indices])
            length_weight_items = length_weight.items()
            length_weight_items.sort(key = (lambda x : -x[1]))
            cum_weights = np.cumsum([x[1] for x in length_weight_items])
            max_length = filter(lambda i : cum_weights[i] <= 1.0 - epsilon, range(len(cum_weights)))[-1]
            good_indices = filter(lambda i : len(strings[i]) <= max_length, range(len(strings)))
            freqs = [freqs[i] for i in good_indices]
            strings = [' '.join(strings[i]) for i in good_indices]
        return dict(zip(strings, freqs))

    def draw_grammar(self,
                     file_path,
                     threshold = 0):
        root_color = 'grey'
        transmission_color = '#FF9900'
        emission_color = '#6699FF'
        left_color = 'orange'
        right_color = 'blue'
        rule_color = '#9999FF'
        graph = pydot.Dot(graph_type='digraph')
        if not self.rules_mapped:
            self.map_rules()
        print len(self.rules)
        rule_nodes = {}
        derivation_nodes = {}
        for rule_index in self.rules.keys():
            if rule_index == self.root_index:
                rule_nodes[rule_index] = pydot.Node('Root',
                                               style = 'filled',
                                               shape = 'triangle',
                                               fillcolor = root_color)
            else:
                rule_nodes[rule_index] = pydot.Node('Rule %d' % rule_index,
                                                style = 'filled',
                                                shape = 'triangle',
                                                fillcolor = transmission_color)
            graph.add_node(rule_nodes[rule_index])
        terminal_nodes = {}
        for term, index in self.term_char_to_index.iteritems():
            terminal_nodes[index] = pydot.Node('Term %s' % str(term),
                                               style = 'filled',
                                               shape = 'ellipse',
                                               fillcolor = emission_color)
            graph.add_node(terminal_nodes[index])
        for rule_index, (pairs, pair_weights,
                         terms, term_weights) in self.rules.iteritems():
            total_weight = np.sum(self.A[rule_index]) + np.sum(self.B[rule_index])
            first_derivation = True
            for i in xrange(len(pairs)):
                if first_derivation:
                    derivation_nodes[rule_index] = {}
                    first_derivation = False
                if pair_weights[i] < threshold * total_weight:
                    continue
                derivation_nodes[rule_index][i] = pydot.Node('%d->%d,%d' % (i, pairs[i][0], pairs[i][1]),
                                                style = 'filled',
                                                fillcolor = rule_color,
                                                shape = 'box')
                graph.add_node(derivation_nodes[rule_index][i])
                edge = pydot.Edge(rule_nodes[rule_index], 
                                  derivation_nodes[rule_index][i])
                edge.set_label('%.2f ' % (pair_weights[i]))
                graph.add_edge(edge)
                edge = pydot.Edge(derivation_nodes[rule_index][i], 
                                  rule_nodes[pairs[i][0]])
                edge.set_label('left')
                edge.set_color(left_color)
                graph.add_edge(edge)
                edge = pydot.Edge(derivation_nodes[rule_index][i], 
                                  rule_nodes[pairs[i][1]])
                edge.set_label('right')
                edge.set_color(right_color)
                graph.add_edge(edge)
            for i in xrange(len(terms)):
                if term_weights[i] < threshold * total_weight:
                    continue
                edge = pydot.Edge(rule_nodes[rule_index],
                                  terminal_nodes[self.term_char_to_index[terms[i]]])
                edge.set_label('%.2f' % term_weights[i])
                edge.set_color(emission_color)
                graph.add_edge(edge)
        graph.write_png(file_path)
        
    def compute_internal_distance_matrix(self, n_samples):
        self.internal_distances = compute_distance_matrix(self, 
                                                          self, 
                                                          n_samples)
        self.ranked_internal_distances = [[(i, j), self.internal_distances[i, j]]
                                          if i != j else [(i, j), np.inf]
                                          for i in xrange(self.N)
                                          for j in xrange(self.N)]
        self.ranked_internal_distances.sort(key = (lambda x : x[1]))
        return self.internal_distances
    
    def merge_on_closest(self):
        assert(len(self.internal_distances) > 0)
        [(first_index, second_index), dist] = self.ranked_internal_distances[0]
        print '\n'
        print '---------- MERGING %d and %d -----------' % (first_index, second_index)
        print self.A.shape
        print self.B.shape
        print self.ranked_internal_distances
        print '\n'
        self.merge(first_index, second_index)
        
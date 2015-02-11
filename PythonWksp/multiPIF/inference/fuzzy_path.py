'''
Created on Feb 10, 2015

    Encapsulation class for a probabilistic path
        representation

@author: Francois Belletti
'''

import numpy as np

from geo_network import Geo_network

## Maximum number of candidate projections for a given node onto the network
MAX_PROJ_NUMBER = 5
MAX_CAND_PATHS  = 3

## A class dedicated to representing paths with uncertainty
#    on the nodes that were used in the network and the links
#    that were used between these nodes.
class Fuzzy_path:
    
    ## @var network
    #    A Geo_network instance.
    network         = None
    ## @var gps_meas
    #    The gps measurement the inference will feed on.
    gps_meas        = np.zeros(0, dtype = np.double)
    ## @var gps_potials
    #    The gps measurement likelihoods as projected onto
    #        the geo network. Each column is a step on the path containing
    #        the corresponding candidate projections' potentials (or likelihoods)
    gps_potials     = np.zeros(0, dtype = np.double)
    ## @var gps_proj_ids
    #    Ids of the nodes gps measurements are projected onto.
    #        Each column is a step on the path containing
    #        the corresponding candidate projections' node ids in the network
    proj_ids        = np.zeros(0, dtype = np.int)
    ## @@var path_potials
    #    List of 3d numpy arrays that represent the potentials (or likelihoods)
    #        of the paths between projection candidates along the path
    path_potials    = [] 
    
    ## The class constructor.
    #    @param geo_n         A Geo_network object.
    #    @param gps_meas      A list of gps [lon, lat] traces.
    #    @param gps_sigma_m   GPS stdev in meters.
    #    @param max_speed     Maximum speed of the agent in m/s
    #    @param delta_ts      Temporal sampling gaps in seconds
    #                            (np array of doubles)
    def __init__(self, geo_n, gps_meas, gps_sigma_m,
                 max_speed, delta_ts, eta):
        self.network        = geo_n
        self.gps_meas       = gps_meas
        n_steps             = len(self.gps_meas)
        self.gps_potials    = np.zeros((MAX_PROJ_NUMBER, n_steps), dtype = np.double)
        self.proj_ids       = np.zeros((MAX_PROJ_NUMBER, n_steps), dtype = np.int)
        #    Compute gps likelihoods
        for step, x in enumerate(gps_meas):
            dist_info                   = geo_n.dist_to_all_nds(x[0], x[1])
            dist_info.sort(key          = (lambda x : x['dist']))
            dist_info                   = dist_info[:MAX_PROJ_NUMBER]
            self.gps_potials[:,step]    = [x['dist'] for x in dist_info]
            self.gps_potials[:,step]    = np.exp( - 0.5 * (self.gps_potials[:,step] 
                                                       / gps_sigma_m) ** 2)
            self.proj_ids[:,step]       = [x['id'] for x in dist_info]
            if step == 0: 
                continue # Need not compute path potentials
            #    Array of potentials between candidates of step i and j
            temp_pot                    = np.zeros((MAX_PROJ_NUMBER, 
                                                    MAX_PROJ_NUMBER,
                                                    MAX_CAND_PATHS),
                                                    dtype = np.double)
            for i in xrange(MAX_PROJ_NUMBER):
                for j in xrange(MAX_PROJ_NUMBER):
                    all_costs           = self.network.find_all_paths(self.proj_ids[i, step - 1],
                                                                      self.proj_ids[j, step],
                                                                      delta_ts[step - 1] * max_speed,
                                                                      k_max = MAX_CAND_PATHS)['costs']
                    k                   = len(all_costs)
                    temp_pot[i,j,:]     = np.inf # Replace non found path by infinte distance
                    temp_pot[i,j,:k]    = all_costs
                    temp_pot[i,j,:]     = np.exp( - eta * temp_pot[i,j,:])
            self.path_potials.append(temp_pot) 
                    
                    
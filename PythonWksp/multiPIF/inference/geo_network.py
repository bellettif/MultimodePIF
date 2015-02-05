'''
Created on Jan 6, 2015

    Class that encapsulates a node to node network
    representation dictionary

@author: Francois Belletti
'''

from matplotlib import pyplot as plt
import numpy as np
import csv

from OSM.misc.geoTools          import computeDist
from k_shortest_thr_c           import compute_k_shortest_threshold

K_MAX = 10

class Geo_network:
    
    #    Entire network with OSM info
    lkd_nds         = {}
    #    Numpy representation for MPIF
    node_ids        = np.zeros(0, dtype = np.int)
    node_lons       = np.zeros(0, dtype = np.double)
    node_lats       = np.zeros(0, dtype = np.double)
    neigh_origins   = np.zeros(0, dtype = np.int)
    neigh_dests     = np.zeros(0, dtype = np.int)
    edge_weights    = np.zeros(0, dtype = np.double)
    #
    node_features   = []
    neighbours      = {}
    
    
    def __init__(self, linked_nodes):
        #    Build OSM network
        for datum in linked_nodes:
            self.lkd_nds[datum['properties']['osm_id']] = {
                'lon'   : datum['geometry']['coordinates'][0],
                'lat'   : datum['geometry']['coordinates'][1],
                'neigh' : datum['properties']['neighbors']}
        #    Build numpy representation
        self.node_ids   = np.asarray(self.lkd_nds.keys(), dtype = np.int)
        self.node_lons  = np.asarray([self.lkd_nds[id]['lon'] for id in self.node_ids])
        self.node_lats  = np.asarray([self.lkd_nds[id]['lon'] for id in self.node_ids])
        temp = []
        for nd_id, nd_info in self.lkd_nds.iteritems():
            for x in nd_info['neigh']:
                if x['osm_id'] in self.lkd_nds:
                    temp.append([nd_id, x['osm_id'], x['edge_info']['length']])
        temp = np.asanyarray(temp)
        self.neigh_origins  = np.ascontiguousarray(temp[:,0], dtype = np.int)
        self.neigh_dests    = np.ascontiguousarray(temp[:,1], dtype = np.int)
        self.edge_weights   = np.ascontiguousarray(temp[:,2], dtype = np.double)
        #
        self.node_features = []
        for nd_id, nd_info in self.lkd_nds.iteritems():
            self.node_features.append([nd_id, nd_info['lon'], nd_info['lat']])
        for nd_id, nd_info in self.lkd_nds.iteritems():
            for x in nd_info['neigh']:
                if x['osm_id'] in self.lkd_nds:
                    if nd_id not in self.neighbours:
                        self.neighbours[nd_id] = []
                    self.neighbours[nd_id].append([x['osm_id'], x['edge_info']['length']])
        
    def plot(self, ax, highlight_nodes = []):
        for nd_id, nd_desc in self.lkd_nds.iteritems():
            nd_lat = nd_desc['lat']
            nd_lon = nd_desc['lon']
            for neigh in nd_desc['neigh']:
                neigh_id = neigh['osm_id']
                neigh_lon = self.lkd_nds[neigh_id]['lon']
                neigh_lat = self.lkd_nds[neigh_id]['lat']
                ax.plot([nd_lon, neigh_lon], [nd_lat, neigh_lat], c = 'grey', lw = 0.5)
        if len(highlight_nodes) > 0:
            longitudes = [self.lkd_nds[nd_id]['lon'] 
                          for nd_id
                          in highlight_nodes]
            latitudes  =  [self.lkd_nds[nd_id]['lat'] 
                          for nd_id
                          in highlight_nodes]
            ax.scatter(longitudes, latitudes)
                
    #
    #    Upper_bound must be in meters
    #    Make the assumption that edges are unique (one to one)
    #
    def find_all_paths(self, start, end, upper_bound):
        #
        return compute_k_shortest_threshold(K_MAX,
                                            upper_bound,
                                            start,
                                            end,
                                            self.node_ids,
                                            self.node_lons,
                                            self.node_lats,
                                            self.neigh_origins,
                                            self.neigh_dests,
                                            self.edge_weights)
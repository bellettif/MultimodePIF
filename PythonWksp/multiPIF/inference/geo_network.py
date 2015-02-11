'''
Created on Jan 6, 2015

    Class that encapsulates a node to node network
    representation dictionary

@author: Francois Belletti
'''

## @package geo_network
#    This package is dedicated to dealing with geographical
#    network data such as osm.

from matplotlib import pyplot as plt
import numpy as np
import csv

from OSM.misc.geoTools          import computeDist
from k_shortest_thr_c           import compute_k_shortest_threshold

## Maximum number shortest path that can be searched in k shortest paths
K_MAX = 10

## Geo_network is a wrapper for osm data with embedded methods for
#    path and mode inference.
#
class Geo_network:
    
    ## @var lkd_nds 
    #    Entire network with OSM info.
    lkd_nds         = {}
    ## @var node_ids
    #    Numpy array of node ids.
    node_ids        = np.zeros(0, dtype = np.int)
    ## @var node_lons
    #    Numpy array of node longitudes.
    node_lons       = np.zeros(0, dtype = np.double)
    ## @var node_lats
    #    Numpy array of node latitudes.
    node_lats       = np.zeros(0, dtype = np.double)
    ## @var neigh_origins
    #    Numpy array of origins in edge table.
    neigh_origins   = np.zeros(0, dtype = np.int)
    ## @var neigh_dests
    #    Numpy array of desitnation in edge table.
    neigh_dests     = np.zeros(0, dtype = np.int)
    ## @var edge_weights
    #    Numpy array of weights in edge table.
    edge_weights    = np.zeros(0, dtype = np.double)
    ## @var node_features
    #    List array of node features, ie [lon, lat].
    node_features   = []
    ## @var neighbours
    #    Dict of list repr of node neighbours, ie [origin] = [[dest, edge_weight] etc].
    neighbours      = {}
    
    ## Constructor
    # @param linked_nodes
    #    List of node data dictionaries at least containing fields \n
    #        ['properties']['osm_id'] which is a unique id for nodes, \n
    #        ['geometry']['coordinates'] = [lon, lat], \n
    #        ['properties']['neighbors'] = [{'osm_id' : dest_osm_id, 'edge_info' : {'length' : l}}]].
    def __init__(self, linked_nodes):
        #    Build OSM network
        for datum in linked_nodes:
            self.lkd_nds[datum['properties']['osm_id']] = {
                'lon'   : datum['geometry']['coordinates'][0],
                'lat'   : datum['geometry']['coordinates'][1],
                'neigh' : datum['properties']['neighbors']}
        #    Build numpy representation
        self.node_ids   = np.asarray(self.lkd_nds.keys(), dtype = np.int)
        self.node_idxs  = dict(zip(self.node_ids, xrange(len(self.node_ids))))
        self.node_lons  = np.asarray([self.lkd_nds[i]['lon'] for i in self.node_ids])
        self.node_lats  = np.asarray([self.lkd_nds[i]['lat'] for i in self.node_ids])
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
    
    ## Plot the network and show the list of nodes in highlight_nodes
    #    @param ax A matplotlib ax instance
    #    @param highlight_nodes A list of node ids to highlight on the plot
    def plot(self, ax, highlight_nodes = [], 
                        mark_positions = [],
                        zoom = False):
        for nd_id, nd_desc in self.lkd_nds.iteritems():
            nd_lat = nd_desc['lat']
            nd_lon = nd_desc['lon']
            for neigh in nd_desc['neigh']:
                neigh_id = neigh['osm_id']
                neigh_lon = self.lkd_nds[neigh_id]['lon']
                neigh_lat = self.lkd_nds[neigh_id]['lat']
                ax.plot([nd_lon, neigh_lon], [nd_lat, neigh_lat], c = 'grey', lw = 0.5)
        if zoom:
            min_lon = np.inf
            max_lon = -np.inf
            min_lat = np.inf
            max_lat = -np.inf
        if len(highlight_nodes) > 0:
            longitudes = [self.lkd_nds[nd_id]['lon'] 
                          for nd_id
                          in highlight_nodes]
            latitudes  = [self.lkd_nds[nd_id]['lat'] 
                          for nd_id
                          in highlight_nodes]
            ax.scatter(longitudes, latitudes)
            if zoom:
                min_lon = min(longitudes)
                max_lon = max(longitudes)
                min_lat = min(latitudes)
                max_lat = max(latitudes)
        if len(mark_positions) > 0:
            longitudes = [x[0] for x in mark_positions]
            latitudes  = [x[1] for x in mark_positions]
            ax.scatter(longitudes, latitudes, marker = 'x')
            if zoom:
                min_lon = min(min(longitudes), min_lon)
                max_lon = max(max(longitudes), max_lon)
                min_lat = min(min(latitudes), min_lat)
                max_lat = max(max(latitudes), max_lon)
        if zoom:
            ax.set_xlim((min_lon, max_lon))
            ax.set_ylim((min_lat, max_lat))
            
    ## Plot the network and show the list of nodes in highlight_nodes
    #    @param ax A matplotlib ax instance
    #    @param highlight_nodes A list of node ids to highlight on the plot
    def plot_path(self, ax, path_nodes = [], 
                            mark_positions = [],
                            zoom = False):
        for nd_id, nd_desc in self.lkd_nds.iteritems():
            nd_lat = nd_desc['lat']
            nd_lon = nd_desc['lon']
            for neigh in nd_desc['neigh']:
                neigh_id = neigh['osm_id']
                neigh_lon = self.lkd_nds[neigh_id]['lon']
                neigh_lat = self.lkd_nds[neigh_id]['lat']
                ax.plot([nd_lon, neigh_lon], [nd_lat, neigh_lat], c = 'grey', lw = 0.5)
        if zoom:
            min_lon = np.inf
            max_lon = -np.inf
            min_lat = np.inf
            max_lat = -np.inf
        if len(path_nodes) > 0:
            longitudes  = [self.lkd_nds[nd_id]['lon'] 
                          for nd_id
                          in path_nodes]
            longitudes  = np.asarray(longitudes)
            latitudes   = [self.lkd_nds[nd_id]['lat'] 
                          for nd_id
                          in path_nodes]
            latitudes   = np.asarray(latitudes)
            ax.quiver(longitudes[:-1], 
                      latitudes[:-1], 
                      longitudes[1:] - longitudes[:-1],
                      latitudes[1:] - latitudes[:-1], 
                      scale_units = 'xy', angles = 'xy', scale = 1)
            if zoom:
                min_lon = min(longitudes)
                max_lon = max(longitudes)
                min_lat = min(latitudes)
                max_lat = max(latitudes)
        if len(mark_positions) > 0:
            longitudes = [x[0] for x in mark_positions]
            latitudes  = [x[1] for x in mark_positions]
            ax.scatter(longitudes, latitudes, marker = 'x')
            if zoom:
                min_lon = min(min(longitudes), min_lon)
                max_lon = max(max(longitudes), max_lon)
                min_lat = min(min(latitudes), min_lat)
                max_lat = max(max(latitudes), max_lon)
        if zoom:
            ax.set_xlim((min_lon, max_lon))
            ax.set_ylim((min_lat, max_lat))
            
                
    ## Find K_MAX shortest path with length below upper_bound
    # @param start Unique id of start node in path search
    # @param end Unique id of end node in path search
    # @param upper_bound Maximum distance that is authorized for paths being searched
    # @param k_max Maximum number of paths that will be searched for
    # @return list of dicts {'costs' : list of path dists, \n 'paths' : list of paths },
    #    \n each path is a list of point ids. \n Paths are ordered by increasing cost.
    def find_all_paths(self, start, end, upper_bound, k_max = K_MAX):
        return compute_k_shortest_threshold(k_max,
                                            upper_bound,
                                            start,
                                            end,
                                            self.node_ids,
                                            self.node_lons,
                                            self.node_lats,
                                            self.neigh_origins,
                                            self.neigh_dests,
                                            self.edge_weights)
    
    ## Generate noisy observations from a random path
    #
    def generate_random_path(self, gps_sigma, n_steps, eta):
        start       = np.random.choice(self.lkd_nds.keys(),
                                       size = 1)[0]
        positions   = []
        node_ids    = [start]
        #
        init_lon = self.lkd_nds[start]['lon'] + \
                    np.random.normal(0.0, gps_sigma)
        init_lat = self.lkd_nds[start]['lat'] + \
                    np.random.normal(0.0, gps_sigma)
        #
        positions.append([init_lon, init_lat])
        #
        for i in xrange(n_steps - 1):
            neighbors   =   self.neighbours[start]
            neigh_ids   =   [x[0] for x in neighbors]
            neigh_dist  =   np.asarray([x[1] for x in neighbors],
                                       np.double)
            neigh_pot   =   np.exp(- eta * neigh_dist)
            neigh_pot   /=  np.sum(neigh_pot)
            next_node   =   np.random.choice(neigh_ids, 
                                             size = 1, 
                                             p = neigh_pot)[0]
            #    We want a loopless path
            n_trials    = 0
            while next_node in node_ids and n_trials < 10:
                next_node   =   np.random.choice(neigh_ids, 
                                             size = 1, 
                                             p = neigh_pot)[0]
                n_trials += 1
            lon = self.lkd_nds[next_node]['lon'] + \
                    np.random.normal(0.0, gps_sigma)
            lat = self.lkd_nds[next_node]['lat'] + \
                    np.random.normal(0.0, gps_sigma)
            node_ids.append(next_node)
            positions.append([lon, lat])
            start = next_node
        return {'actual_ids' : node_ids,
                'gps_meas'   : positions}
            
    def dist_to_all_nds(self, lon, lat):
        ## Needs optimization, write a numpy version of computeDist
        return map((lambda i : {'id' : self.node_ids[i],
                                'dist' : computeDist(lon, 
                                                     lat,
                                                     self.node_lons[i], 
                                                     self.node_lats[i])}),
                   range(len(self.node_ids)))
        
        
        
        
        
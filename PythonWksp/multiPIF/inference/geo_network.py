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
                ax.plot([nd_lon, neigh_lon], [nd_lat, neigh_lat])
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
                
import cPickle as pickle

linked_nodes = pickle.load(open('../tempData/tempBerkeley.pi', 'rb'))

my_network = Geo_network(linked_nodes)

with open('nodes.csv', 'wb') as csv_file:
    csv_writer = csv.writer(csv_file)
    for i, node_feat in enumerate(my_network.node_features):
        csv_writer.writerow([node_feat[0], node_feat[1], node_feat[2]])

with open('neighbours.csv', 'wb') as csv_file:
    csv_writer = csv.writer(csv_file)
    for i, neigh_feat in my_network.neighbours.iteritems():
        for x in neigh_feat:
            csv_writer.writerow([i, x[0], x[1]])


for nd_id in my_network.node_ids:
    if nd_id not in my_network.node_ids:
        print "Dead end"

for neigh_origin in my_network.neigh_origins:
    if neigh_origin not in my_network.node_ids:
        print "Ill defined graph"
        
for neigh_dest in my_network.neigh_dests:        
    if neigh_dest not in my_network.node_ids:
        print "Ill defined graph"
        
start = my_network.lkd_nds.keys()[0]
end   = 240469798

print my_network.lkd_nds[start]

lon_1 = my_network.lkd_nds[start]['lon']
lat_1 = my_network.lkd_nds[start]['lat']

lon_2 = my_network.lkd_nds[end]['lon']
lat_2 = my_network.lkd_nds[end]['lat']

dist = computeDist(lon_1, lat_1, lon_2, lat_2)

path_finding_result = my_network.find_all_paths(start, end, dist * 1.35)

path_points = path_finding_result['paths'][1]

#for path in path_finding_result['paths']:
#    path_points.extend(path)
    
print path_points

fig, (ax1, ax2) = plt.subplots(nrows = 2)
my_network.plot(ax1, [start, end])
my_network.plot(ax2, path_points)
plt.show()
'''
Created on Feb 5, 2015

    Example of how to run path finding in Berkeley

@author: Francois Belletti
'''

import cPickle as pickle
import csv
import numpy as np
from matplotlib import pyplot as plt
import sys

sys.path.append('../')

from OSM.misc.geoTools  import computeDist
from geo_network        import Geo_network
from fuzzy_path         import Fuzzy_path
from extended_viterbi   import Extended_Viterbi


#
#    Load Berkeley road network from pickled file
#
linked_nodes = pickle.load(open('../tempData/tempBerkeley.pi', 'rb'))

#
#    Create corresponding Geo_network object (see class documentation)
#
my_network = Geo_network(linked_nodes)


#===============================================================================
#
#    For c++ debugging
#
# with open('nodes.csv', 'wb') as csv_file:
#     csv_writer = csv.writer(csv_file)
#     for i, node_feat in enumerate(my_network.node_features):
#         csv_writer.writerow([node_feat[0], node_feat[1], node_feat[2]])
# 
# with open('neighbours.csv', 'wb') as csv_file:
#     csv_writer = csv.writer(csv_file)
#     for i, neigh_feat in my_network.neighbours.iteritems():
#         for x in neigh_feat:
#             csv_writer.writerow([i, x[0], x[1]])
#===============================================================================

#
#    Check that network graph is well defined
#
for nd_id in my_network.node_ids:
    if nd_id not in my_network.node_ids:
        print "Dead end"

for neigh_origin in my_network.neigh_origins:
    if neigh_origin not in my_network.node_ids:
        print "Ill defined graph"
        
for neigh_dest in my_network.neigh_dests:        
    if neigh_dest not in my_network.node_ids:
        print "Ill defined graph"

#
#    Choose two nodes in the network
#
start = my_network.lkd_nds.keys()[0]
end   = 240469798

#
#    Get their latitudes and longitudes
#
lon_1 = my_network.lkd_nds[start]['lon']
lat_1 = my_network.lkd_nds[start]['lat']
lon_2 = my_network.lkd_nds[end]['lon']
lat_2 = my_network.lkd_nds[end]['lat']

#
#    Compute the distance between the two nodes
#
dist = computeDist(lon_1, lat_1, lon_2, lat_2)

#
#    Compute all paths betwoeen start and end whose length is below dist * 1.35
#
path_finding_result = my_network.find_all_paths(start, end, dist * 1.35)

#
#    Extract the ids along the first path (the shortest)
#
path_points = path_finding_result['paths'][1]

#
#    Plot the path onto the network
#
#===============================================================================
# fig, (ax1, ax2) = plt.subplots(nrows = 2)
# my_network.plot(ax1, [start, end])
# my_network.plot(ax2, path_points)
# plt.savefig('Example berkeley.png', dpi = 600)
# plt.close()
#===============================================================================

#
# Gps std in lon, lat
gps_sigma = 0.0001
#
# Gps std in meters
gps_sigma_m = computeDist(0, 0, 
                          np.sqrt(gps_sigma * 0.5), 
                          np.sqrt(gps_sigma * 0.5))
#
# User's sensitivity to distance
eta       = 0.01
#
# Maximum user's speed in meters/second
max_speed = 14.0
#
# Delta t between taking samples
delta_t   = 120

random_path = my_network.generate_random_path(gps_sigma, 
                                              20, 
                                              eta)

n_steps = len(random_path['gps_meas'])

#
#    Plot the path onto the network
#
#===============================================================================
# fig, (ax1, ax2) = plt.subplots(nrows = 2)
# my_network.plot(ax1, random_path['actual_ids'],
#                      random_path['gps_meas'],
#                      zoom = True)
# my_network.plot_path(ax2, random_path['actual_ids'], 
#                           random_path['gps_meas'],
#                           zoom = True)
# plt.savefig('Example berkeley 1.png', dpi = 600)
# plt.close()
#===============================================================================

my_fuzzy_path = Fuzzy_path(my_network,
                           random_path['gps_meas'], 
                           gps_sigma_m,
                           max_speed,
                           np.ones(n_steps - 1, dtype = np.double) * delta_t,
                           eta)

my_extended_viterbi = Extended_Viterbi(my_fuzzy_path.gps_potials,
                                       my_fuzzy_path.path_potials)

my_extended_viterbi.compute_potials()
my_extended_viterbi.normalize_potials()

print my_extended_viterbi.pos_potials
print my_extended_viterbi.path_potials








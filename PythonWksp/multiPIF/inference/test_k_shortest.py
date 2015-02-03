'''
Created on Feb 2, 2015

@author: Francois Belletti
'''

# To be tested with euclidian distance

import numpy as np
import copy

from k_shortest_thr_c import compute_k_shortest_threshold

node_0 = [0, 0.0, 0.0]
node_1 = [1, 0.0, 1.0]
node_2 = [2, 1.0, 1.0]
node_3 = [3, 1.0, 0.0]
node_4 = [4, 1.5, 0.0]
    
nodes = np.asanyarray([node_0, node_1, node_2,
                       node_3, node_4], 
                      dtype = np.double)
    
edge_0_1 = [0, 1, 1.0]
edge_0_3 = [0, 3, 5.0]
edge_1_0 = [1, 0, 1.0]
edge_1_2 = [1, 2, 1.0]
edge_1_3 = [1, 3, 1.5]
edge_2_1 = [2, 1, 1.0]
edge_2_3 = [2, 3, 1.0]
edge_3_0 = [3, 0, 5.0]
edge_3_2 = [3, 2, 1.0]
edge_3_4 = [3, 4, 2.0]
edge_4_3 = [4, 3, 2.0]

edges = np.asanyarray([edge_0_1, edge_0_3, 
                       edge_1_0, edge_1_2, edge_1_3,
                       edge_2_1, edge_2_3,
                       edge_3_0, edge_3_2, edge_3_4,
                       edge_4_3],
                      dtype = np.double)

node_ids       =  nodes[:,0]
node_lons      =  nodes[:,1]
node_lats      =  nodes[:,2]

neigh_origins  =  edges[:,0]
neigh_dests    =  edges[:,1]
edge_weights   =  edges[:,2]

k_max = 10
threshold = 10.0
source_id = 0
sink_id = 4

compute_k_shortest_threshold(k_max,
                             threshold,
                             source_id,
                             sink_id,
                             node_ids,
                             node_lons,
                             node_lats,
                             neigh_origins,
                             neigh_dests,
                             edge_weights)

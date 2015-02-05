'''
Created on Feb 5, 2015

    Example of how to run path finding in Berkeley

@author: Francois Belletti
'''

import cPickle as pickle
import csv
from matplotlib import pyplot as plt

from OSM.misc.geoTools import computeDist
from geo_network import Geo_network

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
plt.savefig('Example berkeley.png', dpi = 600)
plt.close()

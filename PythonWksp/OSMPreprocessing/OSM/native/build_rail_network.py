'''
Created on Jan 5, 2015

    Class to read OSM files in their native XML format

@author: Francois Belletti
'''

DEFAULT_FILEPATH = "/Users/cusgadmin/MultimodePIF/Data/OSM/Berkeley/map.osm.xml"

RAIL_KEY = 'railway'
RAIL_VALUES = ['rail', 'subway']

import numpy as np
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt

from plot_tools import *
from network_tools import *


tree = ET.parse(DEFAULT_FILEPATH) 
root = tree.getroot()

nodes = root.findall('node')
node_ids = [x.get('id') for x in nodes]
node_dict = dict(zip(node_ids, nodes))

ways = root.findall('way')

node_ids = set([x.attrib['id'] for x in nodes])

ref_highways = {}   # Highways refering a given node
highways = []

#
#    Extract all the nodes from the road network
#
highways, ref_highways = extract_edges(ways,
                                       target_key = RAIL_KEY,
                                       target_values = RAIL_VALUES)

#
#    For each highway, split into links w.r.t. to nodes
#        being referred more than once
#
target_features = ['railway'] # User's choice
#
links = split_ways(highways, ref_highways, node_dict, target_features)

#
#    Take the resulting leftmost and rightmost nodes and
#        put them in the node collection to form the set of edges
#
linked_nodes = link_nodes(links, target_features)

#
#    Check that degrees make sense
#
#    degrees = [len(x) for x in linked_nodes.values()]
#    plt.hist(degrees, bins = 10)
#    plt.show()

#
#    Check that network makes sense
#
fig, ax = plt.subplots()
plot_rail_network(node_dict, linked_nodes, ax)
plt.show()

#
#    Reduce the network to those nodes only that are necessary
#
reduce_network(linked_nodes, target_features)
fig, ax = plt.subplots()
plot_rail_network(node_dict, linked_nodes, ax)
plt.show()








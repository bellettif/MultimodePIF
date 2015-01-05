'''
Created on Jan 5, 2015

    Class to read OSM files in their native XML format

@author: Francois Belletti
'''

DEFAULT_FILEPATH = "/Users/cusgadmin/MultimodePIF/Data/OSM/Berkeley/map.osm.xml"

HIGHWAY_KEY = 'highway'
HIGHWAY_VALUES = ['primary', 'secondary', 'tertiary']

import numpy as np
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt

from plot_tools import plot_network

def l2_dist(node_1, node_2):
    lat_1 = float(node_1.get('lat'))
    lon_1 = float(node_1.get('lon'))
    lat_2 = float(node_2.get('lat'))
    lon_2 = float(node_2.get('lon'))
    return np.sqrt((lat_1 - lat_2) ** 2 + (lon_1 - lon_2) ** 2)

tree = ET.parse(DEFAULT_FILEPATH) 
root = tree.getroot()

nodes = root.findall('node')
node_ids = [x.get('id') for x in nodes]
node_dict = dict(zip(node_ids, nodes))

ways = root.findall('way')

node_ids = set([x.attrib['id'] for x in nodes])

ref_ways = {}
highways = []

#
#    Extract all the nodes from the road network
#
for way in ways:
    ref_tags  = way.findall('tag')
    road_network = False
    for ref_tag in ref_tags:
        k = ref_tag.get('k')
        v = ref_tag.get('v')
        if k == HIGHWAY_KEY and v in HIGHWAY_VALUES:
            road_network = True
    if not road_network:
        continue
    else:
        highways.append(way)
    way_id = way.get('id')
    ref_nodes = way.findall('nd')
    for ref_node in ref_nodes:
        node_id = ref_node.get('ref')
        if node_id not in ref_ways:
            ref_ways[node_id] = []
        ref_ways[node_id].append(way_id)
        
#
#    Convenience compute distance function
#
def cmpt_length(node_seq):
    dist = 0
    for i in range(len(node_seq) - 1):
        prev_node = node_dict[node_seq[i].get('ref')]
        next_node = node_dict[node_seq[i+1].get('ref')]
        dist += l2_dist(prev_node, next_node)
    return dist

#
#    For each highway, split into links w.r.t. to nodes
#        being referred more than once
#   
links = []
for highway in highways:
    highway_type = None
    max_speed = None
    for tag in highway.findall('tag'):
        k = tag.get('k')
        v = tag.get('v')
        if k == HIGHWAY_KEY and v in HIGHWAY_VALUES:
            highway_type = v
        elif k == 'maxspeed':
            max_speed = v
    node_seq = highway.findall('nd')
    ref_seq = [len(ref_ways[x.get('ref')]) for x in node_seq]
    cut_indices = []
    ref_seq_len = len(ref_seq)
    for i, n_ref in enumerate(ref_seq):
        if n_ref > 1 and (i != 0) and (i != (ref_seq_len - 1)):
            cut_indices.append(i)
    sub_links = []
    cut_indices_len = len(cut_indices)
    if cut_indices_len > 0:
        for i, cut_index in enumerate(cut_indices):
            if i == 0:
                sub_seq = node_seq[:cut_index + 1]  # reach for 1 more to create overlap
                sub_seq_length = cmpt_length(sub_seq)
                sub_links.append({'length'       : sub_seq_length,    #in meters
                                  'max_speed'    : max_speed,
                                  'highway_type' : highway_type,
                                  'node_seq'     : sub_seq})
            if i < (cut_indices_len - 1):
                sub_seq = node_seq[cut_index:cut_indices[i+1] + 1]
                sub_seq_length = cmpt_length(sub_seq)
                sub_links.append({'length'       : sub_seq_length,    #in meters
                                  'max_speed'    : max_speed,
                                  'highway_type' : highway_type,
                                  'node_seq'     : sub_seq})
            if i == (cut_indices_len - 1):
                sub_seq = node_seq[cut_index:]
                sub_seq_length = cmpt_length(sub_seq)
                sub_links.append({'length'       : sub_seq_length,    #in meters
                                  'max_speed'    : max_speed,
                                  'highway_type' : highway_type,
                                  'node_seq'     : sub_seq})
    else:
        sub_seq = node_seq
        sub_seq_length = cmpt_length(sub_seq)
        sub_links = [{'length'       : sub_seq_length,    #in meters
                      'max_speed'    : max_speed,
                      'highway_type' : highway_type,
                      'node_seq'     : sub_seq}]
    print sub_links
    links.extend(sub_links)
    
#
#    Take the resulting leftmost and rightmost nodes and
#        put them in the node collection
#
linked_nodes = {}
for link in links:
    leftmost_node_id  = link['node_seq'][0].get('ref')
    rightmost_node_id = link['node_seq'][-1].get('ref')
    # The following work on the set of features
    #     needs to become dynamic
    highway_type = link['highway_type']
    length       = link['length']
    max_speed    = link['max_speed']
    #
    #    Create edges in graph (vertices are keys)
    #    So far one ways are not taken into account
    #
    # Link left to right
    if leftmost_node_id not in linked_nodes:
        linked_nodes[leftmost_node_id] = {}
    linked_nodes[leftmost_node_id][rightmost_node_id] = \
        {'highway_type' : highway_type,
         'length'       : length,
         'max_speed'    : max_speed}
    # Link right to left
    if rightmost_node_id not in linked_nodes:
        linked_nodes[rightmost_node_id] = {}
    linked_nodes[rightmost_node_id][leftmost_node_id] = \
        {'highway_type' : highway_type,
         'length'       : length,
         'max_speed'    : max_speed}
        
print linked_nodes

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
plot_network(node_dict, linked_nodes, ax)
plt.show()



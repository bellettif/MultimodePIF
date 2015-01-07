'''
Created on Jan 5, 2015

    Class to read OSM files in their native XML format

@author: Francois Belletti
'''

INPUT_FILEPATH = "/Users/cusgadmin/MultimodePIF/Data/OSM/Berkeley/map.osm.xml"
OUTPUT_FILEPATH = "/Users/cusgadmin/MultimodePIF/Data/OSM/Berkeley/network.geojson"

HIGHWAY_KEY = 'highway'
HIGHWAY_VALUES = ['primary', 'secondary', 'tertiary']

DEFAULT_MAX_SPEEDS = {'primary' : 55.0,
                      'secondary' : 25.0,
                      'tertiary' : 25.0}

import xml.etree.ElementTree as ET
import json
import numpy as np
from matplotlib import pyplot as plt

from plot_tools import *
from network_tools import *


tree = ET.parse(INPUT_FILEPATH)
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
                                       target_key = HIGHWAY_KEY,
                                       target_values = HIGHWAY_VALUES)

#
#    For each highway, split into links w.r.t. to nodes
#        being referred more than once
#
target_features = ['maxspeed', 'highway'] # User's choice
#
links = split_ways(highways, ref_highways, node_dict, target_features)

#
#    Take the resulting leftmost and rightmost nodes and
#        put them in the node collection to form the set of edges
#
linked_nodes = link_nodes(links, target_features)

data = []
for node_id, neigh_dict in linked_nodes.iteritems():
    osm_node = node_dict[node_id]
    # Extract node info
    osm_id = int(node_id)
    lon = float(osm_node.get('lon'))
    lat = float(osm_node.get('lat'))
    neigh_list = []
    for neigh_id, edge_desc in neigh_dict.iteritems():
        neigh_list.append({"osm_id"    : int(neigh_id),
                           "edge_info" : {
                                "length"   : edge_desc['length'],
                                "maxspeed" : float(edge_desc['maxspeed'].split(' ')[0])
                                    if edge_desc['maxspeed'] != None 
                                    else DEFAULT_MAX_SPEEDS[edge_desc['highway']],
                                "highway"  : edge_desc['highway']}})
    datum = {"properties" : {
                "osm_id"   : osm_id,
                "neighbors" : neigh_list},
             "geometry" : {
                "type" : "Point",
                "coordinates" : [lon, lat]}}
    data.append(datum)
    
#
#    Temporary
#
import cPickle as pickle
pickle.dump(data, open('../../tempData/tempBerkeley.pi', 'wb'))
   
#
#    Format is not good, need to investigate
#
geojson_dump = {"type": "FeatureCollection",
                "crs": {
                    "type": "name", 
                    "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" }}, 
                "features":
                    data}

json.dump(geojson_dump, open(OUTPUT_FILEPATH, 'wb'))

#
#    Check that degrees make sense
#
#    degrees = [len(x) for x in linked_nodes.values()]
#    plt.hist(degrees, bins = 10)
#    plt.show()

#
#    Check that network makes sense
#
#fig, ax = plt.subplots()
#plot_road_network(node_dict, linked_nodes, ax)
#plt.show()

#
#    Reduce the network to those nodes only that are necessary
#
#reduce_network(linked_nodes, target_features)
#fig, ax = plt.subplots()
#plot_road_network(node_dict, linked_nodes, ax)
#plt.show()
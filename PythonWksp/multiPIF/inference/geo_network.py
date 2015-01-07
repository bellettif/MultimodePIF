'''
Created on Jan 6, 2015

    Class that encapsulates a node to node network
    representation dictionary

@author: Francois Belletti
'''

from copy import deepcopy
from matplotlib import pyplot as plt


class Geo_network:
    #
    lkd_nds = {}
    #
    def __init__(self, linked_nodes):
        for datum in linked_nodes:
            self.lkd_nds[datum['properties']['osm_id']] = {
                'lon'   : datum['geometry']['coordinates'][0],
                'lat'   : datum['geometry']['coordinates'][1],
                'neigh' : datum['properties']['neighbors']}
    #    
    def plot(self, ax):
        for nd_id, nd_desc in self.lkd_nds.iteritems():
            nd_lat = nd_desc['lat']
            nd_lon = nd_desc['lon']
            for neigh in nd_desc['neigh']:
                neigh_id = neigh['osm_id']
                neigh_lat = self.lkd_nds[neigh_id]['lat']
                neigh_lon = self.lkd_nds[neigh_id]['lon']
                ax.plot([nd_lon, neigh_lon], [nd_lat, neigh_lat])
                
                
import cPickle as pickle

linked_nodes = pickle.load(open('../tempData/tempBerkeley.pi', 'rb'))

my_network = Geo_network(linked_nodes)

fig, ax = plt.subplots()

my_network.plot(ax)

plt.show()
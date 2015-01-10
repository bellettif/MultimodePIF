'''
Created on Jan 6, 2015

    Class that encapsulates a node to node network
    representation dictionary

@author: Francois Belletti
'''

from copy import deepcopy
from matplotlib import pyplot as plt
from collections import deque

from OSM.misc.geoTools import computeDist

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
        final_paths = []
        #
        active_paths = set()
        active_paths.add('%d_%f' % (start, 0.0))
        #
        end_lon = self.lkd_nds[end]['lon']
        end_lat = self.lkd_nds[end]['lat']
        def dist_to_dest(nd_id):
            return computeDist(self.lkd_nds[nd_id]['lon'],
                               self.lkd_nds[nd_id]['lat'],
                               end_lon,
                               end_lat)
        #
        while len(active_paths) > 0:
            print len(active_paths)
            print active_paths
            print '\n'
            current_path = active_paths.pop().split('_')
            nd_ids = current_path[:-1]
            nd_id = int(nd_ids[-1])
            dist = float(current_path[-1])
            path_id = '_'.join(nd_ids)
            nexts = self.lkd_nds[nd_id]['neigh']
            for next_nd in nexts:
                next_id = next_nd['osm_id']
                if next_id == nd_id:
                    continue
                if next_id != end:
                    if str(next_id) in nd_ids:
                        # Looping path, discard
                        continue
                    min_dist_to_dest = dist_to_dest(next_id)
                    if (dist + min_dist_to_dest) > upper_bound :
                        # This path cannot be admissible
                        continue
                    length = next_nd['edge_info']['length'] 
                    active_paths.add(path_id + '_' + str(next_id) + 
                                     '_' + str(dist + length))
                else:
                    length = next_nd['edge_info']['length']
                    total_dist = length + dist
                    if total_dist > upper_bound:
                        # This path is not admissible, discard it
                        continue
                    else:
                        final_paths.append({'nodes' : path_id + '_' + str(end),
                                            'length' : total_dist})
        return final_paths

                
import cPickle as pickle

linked_nodes = pickle.load(open('../tempData/tempBerkeley.pi', 'rb'))

print linked_nodes

my_network = Geo_network(linked_nodes)

start = 53116963
end   = 240469798

lon_1 = my_network.lkd_nds[start]['lon']
lat_1 = my_network.lkd_nds[start]['lat']

lon_2 = my_network.lkd_nds[end]['lon']
lat_2 = my_network.lkd_nds[end]['lat']

dist = computeDist(lon_1, lat_1, lon_2, lat_2)

paths = my_network.find_all_paths(start, end, dist * 1.35)

print paths
path_points = []
for path in paths:
    path_points.extend(map((lambda x : int(x)), path['nodes'].split('_')))
    
print path_points

fig, (ax1, ax2) = plt.subplots(nrows = 2)
my_network.plot(ax1, [start, end])
my_network.plot(ax2, path_points)
plt.show()





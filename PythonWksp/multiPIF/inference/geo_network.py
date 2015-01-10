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
    #
    def find_all_paths(self, start, end, upper_bound):
        candidate_paths = {}
        candidate_paths[start] = [(str(start), 0.0)]
        #
        final_paths = []
        #
        active_nodes = deque()
        active_nodes.append(start)
        #
        end_lon = self.lkd_nds[end]['lon']
        end_lat = self.lkd_nds[end]['lat']
        def dist_to_dest(nd_id):
            return computeDist(self.lkd_nds[nd_id]['lon'],
                               self.lkd_nds[nd_id]['lat'],
                               end_lon,
                               end_lat)
        #
        while len(active_nodes) > 0:
            print len(active_nodes)
            print active_nodes
            print '\n'
            nd_id = active_nodes.pop()
            nd = self.lkd_nds[nd_id]
            paths = candidate_paths[nd_id]
            nexts = self.lkd_nds[nd_id]['neigh']
            for next_nd in nexts:
                next_id = next_nd['osm_id']
                #print 'Next id = %d' % next_id
                if next_id != end:
                    min_dist_to_dest = dist_to_dest(next_id)
                    for (path_id, dist) in paths:
                        if str(next_id) in path_id.split('_'):
                            #print '\tDiscarding for looping'
                            # Looping path, discard
                            continue
                        if (dist + min_dist_to_dest) > upper_bound :
                            #print '\tDiscarding for heuristic'
                            # This path cannot be admissible
                            continue
                        #print '\tConsidering path'
                        length = next_nd['edge_info']['length'] 
                        if next_id not in candidate_paths:
                            candidate_paths[next_id] = []
                        candidate_paths[next_id].append((path_id +
                                                         '_' +
                                                         str(next_id),
                                                         dist + length))
                        print 'Adding %s to %s' % (next_id, path_id)
                        active_nodes.append(next_id)
                else:
                    length = next_nd['edge_info']['length']
                    for (path_id, dist) in candidate_paths[nd_id]:
                        total_dist = length + dist
                        if total_dist > upper_bound:
                            # This path is not admissible, discard it
                            #print '\tDiscarding from exact distance'
                            continue
                        else:
                            #print '\tFound path %s to %d' % (path_id, end)
                            final_paths.append(path_id + '_' + str(end))
            #del candidate_paths[nd_id]
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

print computeDist(lon_1, lat_1, lon_2, lat_2)

paths = my_network.find_all_paths(start, end, 2000)

print paths
path_points = []
for path in paths:
    path_points.extend(map((lambda x : int(x)), path.split('_')))
    
print path_points

fig, (ax1, ax2) = plt.subplots(nrows = 2)
my_network.plot(ax1, [start, end])
my_network.plot(ax2, path_points)
plt.show()





'''
Created on Jan 4, 2015

    Script to test queries from the ZenMap
    jsonDB. This format is now deprecated.

@author: Francois Belletti
'''

import pymongo
from matplotlib import pyplot as plt

from OSM.zenMap.geo_queries import find_near
from OSM.zenMap.plot_tools import plot_doc

OSM_DB = 'filteredOSM'
HIGHWAY_COLL = 'highways'
ROUTE_COLL = 'routes'
RAILWAY_COLL = 'railways'

client = pymongo.MongoClient()

road_network = client[OSM_DB]
highways = road_network[HIGHWAY_COLL]
routes = road_network[ROUTE_COLL]
railways = road_network[RAILWAY_COLL]

# Downtown berkeley
example_coords = [-122.27, 37.87]

# Emeryville
example_coords = [-122.30, 37.865]

# Downtown SF
example_coords = [-122.40, 37.782]

fig, ax = plt.subplots()
ax.scatter(example_coords[0], example_coords[1])

osm_ids = []
for highway_section in find_near(highways,
                                 example_coords):
    osm_ids.append(highway_section['properties']['osm_id'])
#    plot_doc(ax, highway_section)
    
id_counts = {}
for osm_id in osm_ids:
    if osm_id not in id_counts:
        id_counts[osm_id] = 0
    id_counts[osm_id] += 1
    
print set(id_counts.values())

for railway_section in find_near(railways,
                                 example_coords):
    plot_doc(ax, railway_section)
    
for route_section in find_near(routes,
                               example_coords):
    plot_doc(ax, route_section)    
    
plt.show()


'''
Created on Jan 4, 2015

@author: Francois Belletti
'''

import pymongo
from matplotlib import pyplot as plt

from geo_queries import find_near
from plot_tools import plot_doc

OSM_DB = 'filteredOSM'
HIGHWAY_COLL = 'highways'
ROUTE_COLL = 'routes'
RAILWAY_COLL = 'railways'

client = pymongo.MongoClient()

road_network = client[OSM_DB]
highways = road_network[HIGHWAY_COLL]
routes = road_network[ROUTE_COLL]
railways = road_network[RAILWAY_COLL]

example_coords = [-122.27, 37.87]
example_coords = [-122.40, 37.782]

fig, ax = plt.subplots()
ax.scatter(example_coords[0], example_coords[1])

for highway_section in find_near(highways,
                                 example_coords):
    print highway_section['properties']['highway']
    print highway_section['properties']['route']
    print highway_section['properties']['railway']
    print highway_section['geometry']['type']
    print '\n'
    plot_doc(ax, highway_section)
    
for railway_section in find_near(railways,
                                 example_coords):
    print railway_section['properties']['railway']
    print railway_section['geometry']
    plot_doc(ax, railway_section)
    
for route_section in find_near(routes,
                               example_coords):
    plot_doc(ax, route_section)    
    
plt.show()


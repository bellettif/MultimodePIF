'''
Created on Jan 4, 2015

@author: Francois Belletti
'''

import pymongo

from geo_queries import findNear
from OSM.geo_queries import findNear

OSM_DB = 'filteredOSM'
HIGHWAY_COLL = 'highways'
ROUTE_COLL = 'routes'
RAILWAY_COLL = 'railways'

client = pymongo.MongoClient()

road_network = client[OSM_DB]
highways = road_network[HIGHWAY_COLL]
routes = road_network[ROUTE_COLL]
railways = road_network[RAILWAY_COLL]

example_coords = highways.find_one()['geometry']['coordinates']

for highway_section in findNear(highways,
                                example_coords):
    print 'Coucou'
    print highway_section


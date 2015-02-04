'''
Created on Jan 4, 2015

@author: Francois Belletti
'''

DEFAULT_MAX_DIST = 200

#
#    Coords must be given as [long, lat]
#    Min and max dist are given in meters
#
def find_near(coll,
              coords,
              target_field = 'geometry',
              min_dist = 0,
              max_dist = DEFAULT_MAX_DIST):
    query_value = {'$geoNear': {
                        '$geometry': {'type': "Point", 'coordinates': coords},
                        '$minDistance': min_dist,
                        '$maxDistance': max_dist
                        }
                    }
    return coll.find({target_field : query_value})

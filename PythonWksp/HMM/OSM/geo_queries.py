'''
Created on Jan 4, 2015

@author: Francois Belletti
'''

#
#    Coords must be given as [long, lat]
#    Min and max dist are given in meters
#
def findNear(coll,
             coords,
             target_field = 'geometry',
             min_dist = 0,
             max_dist = 1000):
    query_value = {'$geoNear': {
                        '$geometry': {'type': "Point", 'coordinates': coords},
                        '$minDistance': min_dist,
                        '$maxDistance': max_dist
                        }
                    }
    print query_value
    print coll.find({target_field : query_value}).count()
    return coll.find({target_field : query_value})

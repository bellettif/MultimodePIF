'''
Created on Nov 19, 2014

    Functions related to GPS geolocalization

@author: Francois Belletti
'''
 
 
import numpy as np
from geopy.distance import great_circle
 
## Compute distance between GPS points
#    @param lng_1 Longitude of first point
#    @param lat_1 Latitude of first point
#    @param lng_2 Longitude of second point
#    @param lat_2 Latitude of second point
#    @return Distance in meters
def computeDist(lng_1, lat_1, lng_2, lat_2):
    return great_circle((lat_1, lng_1), (lat_2, lng_2)).meters


'''
Created on Nov 19, 2014

    Functions related to GPS geolocalization

@author: Francois Belletti
'''
 
 
import numpy as np
from geopy.distance import great_circle
 
def computeDist(lng_1, lat_1, lng_2, lat_2):
    return great_circle((lat_1, lng_1), (lat_2, lng_2)).meters
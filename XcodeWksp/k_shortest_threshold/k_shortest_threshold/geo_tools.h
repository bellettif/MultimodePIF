//
//  geo_tools.h
//  k_shortest_threshold
//
//  Created by francois.belletti on 2/2/15.
//  Copyright (c) 2015 francois.belletti. All rights reserved.
//

#ifndef __k_shortest_threshold__geo_tools__
#define __k_shortest_threshold__geo_tools__

#include <stdio.h>
#include <cmath>
#include <vector>

double radians (double d);

double degrees (double r);

//  haversine formula
double geo_dist_(double lon_1, double lat_1,
                 double lon_2, double lat_2);

double geo_dist(std::pair<double, double> xy_1,
                std::pair<double, double> xy_2);

#endif /* defined(__k_shortest_threshold__geo_tools__) */

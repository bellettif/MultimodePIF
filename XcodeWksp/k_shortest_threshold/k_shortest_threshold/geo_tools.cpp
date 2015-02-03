//
//  geo_tools.cpp
//  k_shortest_threshold
//
//  Created by francois.belletti on 2/2/15.
//  Copyright (c) 2015 francois.belletti. All rights reserved.
//

#include <math.h>

#include "geo_tools.h"

double radians (double d) {
    return d * M_PI / 180;
}

double degrees (double r) {
    return r * 180/ M_PI;
}

double geo_dist_(double lon_1, double lat_1,
                 double lon_2, double lat_2){
    double dlon = lon_2 - lon_1;
    double dlat = lat_2 - lat_1;
    double a = std::pow(sin(dlat * 0.5),2) + cos(lat_1) * cos(lat_2) * std::pow(sin(dlon * 0.5),2);
    return 6378100 * 2.0 * asin(sqrt(a));
}

double geo_dist(std::pair<double, double> xy1,
                std::pair<double, double> xy2){
    return geo_dist_(xy1.first, xy1.second, xy2.first, xy2.second);
}
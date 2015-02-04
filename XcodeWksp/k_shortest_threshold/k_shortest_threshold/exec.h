//
//  exec.h
//  k_shortest_threshold
//
//  Created by francois.belletti on 2/2/15.
//  Copyright (c) 2015 francois.belletti. All rights reserved.
//

#ifndef __k_shortest_threshold__exec__
#define __k_shortest_threshold__exec__

#include <stdio.h>
#include <vector>
#include <unordered_map>

#include "graph.h"

void get_k_shortest_threshold(int k_max,
                              double threshold,
                              long source_id,
                              long sink_id,
                              long * ids,
                              double * lons,
                              double * lats,
                              long * neigh_origins,
                              long * neigh_dests,
                              double * neigh_weights,
                              int n_vertices,
                              int n_edges,
                              std::vector<std::vector<long> > & path_results,
                              std::vector<double> & path_costs);



#endif /* defined(__k_shortest_threshold__exec__) */

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
                              int source_id,
                              int sink_id,
                              int * ids,
                              double * lons,
                              double * lats,
                              int * neigh_origins,
                              int * neigh_dests,
                              double * neigh_weights,
                              int n_vertices,
                              int n_edges,
                              std::vector<std::vector<int> > & path_results,
                              std::vector<double> & path_costs);



#endif /* defined(__k_shortest_threshold__exec__) */

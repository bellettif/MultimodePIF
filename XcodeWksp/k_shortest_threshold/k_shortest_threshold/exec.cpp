//
//  exec.cpp
//  k_shortest_threshold
//
//  Created by francois.belletti on 2/2/15.
//  Copyright (c) 2015 francois.belletti. All rights reserved.
//

#include "exec.h"

#include "graph.h"
#include "geo_tools.h"

typedef std::pair<double, double> dou_dou_pair;

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
                              std::vector<double> & path_costs){
    
    std::vector< std::pair<long, dou_dou_pair > > node_features(n_vertices);
    std::unordered_map<long, int> index_conversion;
    
    for(int i = 0; i < n_vertices; ++i){
        //std::cout << "-" << ids[i] << " " << lons[i] << " " << lats[i] << std::endl;
        node_features[i]            =   {ids[i], {lons[i], lats[i]}};
        index_conversion[ids[i]]    =   i;
    }
    
    std::vector< std::vector< std::pair<long, double> > > neighbors(n_vertices);
    
    for(int i = 0; i < n_edges; ++i){
        neighbors[index_conversion[neigh_origins[i]]].push_back({neigh_dests[i], neigh_weights[i]});
    }
    
    std::function<double(dou_dou_pair, dou_dou_pair)> euclidian_norm = [](
                                                                          dou_dou_pair coords_1, dou_dou_pair coords_2){
        return std::sqrt(std::pow(coords_1.first - coords_2.first, 2)
                         +
                         std::pow(coords_1.second - coords_2.second, 2));
    };
    
    Graph<dou_dou_pair, double> main_graph(node_features,
                                           neighbors);
    
    std::vector<Path<double>*> k_best_paths = main_graph.k_shortest_threshold(threshold,
                                                                              k_max,
                                                                              source_id,
                                                                              sink_id,
                                                                              euclidian_norm); // Replace by geo dist for gps
    
    path_results.clear();
    path_results.resize(k_best_paths.size());
    path_costs.clear();
    path_costs.resize(k_best_paths.size());
    
    for(int k = 0; k < k_best_paths.size() ; ++k){
        const std::vector<long> & path_nodes = k_best_paths[k]->get_ids();
        path_results[k].insert(path_results[k].begin(),
                               path_nodes.begin(),
                               path_nodes.end());
        path_costs[k] = k_best_paths[k]->get_cost();
    }
    
    for(auto & x : k_best_paths){
        delete x ;
    }
    

}

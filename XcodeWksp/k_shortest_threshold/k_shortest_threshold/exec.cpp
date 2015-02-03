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
                              std::vector<double> & path_costs){
    
    //std::cout << "Launching" << std::endl;
    
    std::vector< std::pair<int, dou_dou_pair > > node_features(n_vertices);
    std::unordered_map<int, int> index_conversion;
    
    //std::cout << "Filling nodes" << std::endl;
    
    for(int i = 0; i < n_vertices; ++i){
        //std::cout << "-" << ids[i] << " " << lons[i] << " " << lats[i] << std::endl;
        node_features[i]            =   {ids[i], {lons[i], lats[i]}};
        index_conversion[ids[i]]    =   i;
    }
    
    std::vector< std::vector< std::pair<int, double> > > neighbors(n_vertices);
    
    //std::cout << "Filling temp neighbors" << std::endl;
    
    for(int i = 0; i < n_edges; ++i){
        //std::cout << "-" << neigh_origins[i] << std::endl;
        neighbors[index_conversion[neigh_origins[i]]].push_back({neigh_dests[i], neigh_weights[i]});
    }
    
    /*
    std::cout << "Ready" << std::endl;
    for(int i = 0; i < n_vertices; ++i){
        std::cout << node_features[i].first << std::endl;
        for(auto x : neighbors[i]){
            std::cout << x.first << " ";
        }
        std::cout << std::endl;
    }
    */
    
    std::function<double(dou_dou_pair, dou_dou_pair)> euclidian_norm = [](
                                                                          dou_dou_pair coords_1, dou_dou_pair coords_2){
        return std::sqrt(std::pow(coords_1.first - coords_2.first, 2)
                         +
                         std::pow(coords_1.second - coords_2.second, 2));
    };
    
    /*
    std::cout << "Initializing graph" << std::endl;
    std::cout << node_features.size() << std::endl;
    std::cout << neighbors.size() << std::endl;
    */
    
    Graph<dou_dou_pair, double> main_graph(node_features,
                                           neighbors);
    
    //std::cout << "Graph built" << std::endl;
    
    //main_graph.plot();
    
    //std::cout << "Searching for best paths" << std::endl;
    
    std::vector<Path<double>*> k_best_paths = main_graph.k_shortest_threshold(threshold,
                                                                              k_max,
                                                                              source_id,
                                                                              sink_id,
                                                                              euclidian_norm); // Replace by geo dist for gps
    
    //std::cout << "Found " << k_best_paths.size() << " paths" << std::endl;
    
    path_results.clear();
    path_results.resize(k_best_paths.size());
    path_costs.clear();
    path_costs.resize(k_best_paths.size());
    
    for(int k = 0; k < k_best_paths.size() ; ++k){
        const std::vector<int> & path_nodes = k_best_paths[k]->get_ids();
        path_results[k].insert(path_results[k].begin(),
                               path_nodes.begin(),
                               path_nodes.end());
        path_costs[k] = k_best_paths[k]->get_cost();
    }
    
    //std::cout << "Done with k best paths" << std::endl;
    
    for(auto & x : k_best_paths){
        //x->plot();
        delete x ;
    }
    
    //std::cout << "Terminating" << std::endl;

}

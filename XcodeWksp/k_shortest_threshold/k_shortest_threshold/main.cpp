//
//  main.cpp
//  k_shortest_threshold
//
//  Created by francois.belletti on 1/24/15.
//  Copyright (c) 2015 francois.belletti. All rights reserved.
//

#include <iostream>
#include <vector>
#include "Graph.h"

typedef std::pair<double, double>   dou_dou_pair;
typedef std::pair<int, double>      int_dou_pair;

int main(int argc, const char * argv[]) {

    dou_dou_pair coord_0 = {0.0, 0.0};
    dou_dou_pair coord_1 = {0.0, 1.0};
    dou_dou_pair coord_2 = {1.0, 1.0};
    dou_dou_pair coord_3 = {1.0, 0.0};
    dou_dou_pair coord_4 = {1.5, 0.0};
    
    std::vector< std::pair<int, dou_dou_pair> > node_features = {
        {0, coord_0},
        {1, coord_1},
        {2, coord_2},
        {3, coord_3},
        {4, coord_4}
    };
    
    int_dou_pair edge_w_0_1 = {1, 1.0};
    int_dou_pair edge_w_0_3 = {3, 5.0};
    int_dou_pair edge_w_1_0 = {0, 1.0};
    int_dou_pair edge_w_1_2 = {2, 1.0};
    int_dou_pair edge_w_1_3 = {3, 1.5};
    int_dou_pair edge_w_2_1 = {1, 1.0};
    int_dou_pair edge_w_2_3 = {3, 1.0};
    int_dou_pair edge_w_3_0 = {0, 5.0};
    int_dou_pair edge_w_3_4 = {4, 2.0};
    int_dou_pair edge_w_4_3 = {3, 2.0};
    
    std::vector< std::vector<int_dou_pair> > neighbors = {
        {edge_w_0_1, edge_w_0_3},
        {edge_w_1_0, edge_w_1_2, edge_w_1_3},
        {edge_w_2_1, edge_w_2_3},
        {edge_w_3_0, edge_w_3_4},
        {edge_w_4_3}
    };
    
    Graph<dou_dou_pair, double> my_graph (node_features,
                                          neighbors);
    
    my_graph.plot();
    
    std::unordered_map<int,
                       std::unordered_map<int, double>> removed_edges;
    
    dou_dou_pair temp = my_graph.remove_node(2, removed_edges);
    
    my_graph.plot();
    
    my_graph.add_node(2, temp);
    
    my_graph.plot();
    
    for(const auto & xyz : removed_edges){
        for(const auto & yz : xyz.second){
            my_graph.add_edge(xyz.first, yz.first, yz.second);
        }
    }
    
    my_graph.plot();
    
    std::function<double(dou_dou_pair, dou_dou_pair)> euclidian_norm = [](
        dou_dou_pair coords_1, dou_dou_pair coords_2){
        return std::sqrt(std::pow(coords_1.first - coords_2.first, 2)
                         +
                         std::pow(coords_1.second - coords_2.second, 2));
    };
    
    /*
    Path<double>* opt_path = my_graph.A_star_threshold(0, 4, euclidian_norm, 10.0);
    opt_path->plot();
    delete opt_path;
    */
    
    std::vector<Path<double>*> k_best_paths = my_graph.k_shortest_threshold(10.0,
                                                                            2,
                                                                            0,
                                                                            4,
                                                                            euclidian_norm);
    
    std::cout << "Done with k best paths" << std::endl;
    
    for(auto & x : k_best_paths){
        x->plot();
        delete x ;
    }
    
    return 0;
}

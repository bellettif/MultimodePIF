//
//  main.cpp
//  k_shortest_threshold
//
//  Created by francois.belletti on 1/24/15.
//  Copyright (c) 2015 francois.belletti. All rights reserved.
//

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <boost/algorithm/string.hpp>

#include "graph.h"
#include "geo_tools.h"

typedef std::pair<double, double>   dou_dou_pair;
typedef std::pair<long, double>     long_dou_pair;

std::string node_file = "/Users/cusgadmin/MultimodePIF/MultimodePIF/PythonWksp/multiPIF/inference/nodes.csv";
std::string neighbor_file = "/Users/cusgadmin/MultimodePIF/MultimodePIF/PythonWksp/multiPIF/inference/neighbours.csv";


int main(int argc, const char * argv[]) {

    /*
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
    int_dou_pair edge_w_3_2 = {2, 1.0};
    int_dou_pair edge_w_3_4 = {4, 2.0};
    int_dou_pair edge_w_4_3 = {3, 2.0};
    
    std::vector< std::vector<int_dou_pair> > neighbors = {
        {edge_w_0_1, edge_w_0_3},
        {edge_w_1_0, edge_w_1_2, edge_w_1_3},
        {edge_w_2_1, edge_w_2_3},
        {edge_w_3_0, edge_w_3_2, edge_w_3_4},
        {edge_w_4_3}
    };
     */
    
    std::vector< std::pair<long, dou_dou_pair> >     node_features;
    std::unordered_map<long, int>                    id_convert;
    
    std::vector< std::string > buffer;
    
    std::string current_line;
    std::ifstream myfile (node_file);
    int i = 0;
    if (myfile.is_open())
    {
        while ( getline (myfile, current_line) )
        {
            boost::split(buffer, current_line, boost::is_any_of(","));
            id_convert[std::stol(buffer[0])] = i++;
            node_features.push_back({std::stol(buffer[0]),
                                    {std::stod(buffer[1]), std::stod(buffer[2])}});
        }
        myfile.close();
    }
    
    std::vector< std::vector<long_dou_pair> >        neighbors (node_features.size());
    
    std::ifstream myotherfile (neighbor_file);
    i = 0;
    if (myotherfile.is_open())
    {
        while ( getline (myotherfile, current_line) )
        {
            boost::split(buffer, current_line, boost::is_any_of(","));
            neighbors[id_convert[std::stol(buffer[0])]].push_back({std::stol(buffer[1]), std::stod(buffer[2])});
        }
        myotherfile.close();
    }
    

    std::cout << "files loaded" << std::endl;

    
    Graph<dou_dou_pair, double> my_graph (node_features,
                                          neighbors);
    
    //my_graph.plot();
    
    std::function<double(dou_dou_pair, dou_dou_pair)> euclidian_norm = [](
        dou_dou_pair coords_1, dou_dou_pair coords_2){
        return std::sqrt(std::pow(coords_1.first - coords_2.first, 2)
                         +
                         std::pow(coords_1.second - coords_2.second, 2));
    };
    
    std::vector<Path<double>*> k_best_paths = my_graph.k_shortest_threshold(8000.0,
                                                                            4,
                                                                            2820169735,
                                                                            304710548,
                                                                            geo_dist);
    
    std::cout << "Done with k best paths" << std::endl;
    
    for(auto & x : k_best_paths){
        x->plot();
        delete x ;
    }
    
    return 0;
}

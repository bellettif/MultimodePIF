//
//  Graph.h
//  k_shortest_threshold
//
//  Created by francois.belletti on 1/25/15.
//  Copyright (c) 2015 francois.belletti. All rights reserved.
//

#ifndef k_shortest_threshold_Graph_h
#define k_shortest_threshold_Graph_h

#include <unordered_map>
#include <vector>
#include <queue>
#include <set>
#include <functional>
#include <assert.h>



typedef std::unordered_map<int, int>    int_int_map;
typedef std::set<int>                   int_set;


template<typename T1, typename T2>
class Graph{
    
    typedef std::unordered_map<int, T1>             int_T1_map;
    typedef std::unordered_map<int, T2>             int_T2_map;
    typedef std::unordered_map<int, int_T2_map>     int_int_T2_map_map;
    
private:
    
    int_T1_map              m_nodes;
    int_int_T2_map_map      m_edges;
    size_t                      m_N;

public:
    Graph(const std::vector< std::pair<int, T1> > & node_features,
          const std::vector< std::vector< std::pair<int, T2> > > & neighbors){
        
        assert(node_features.size() == neighbors.size());
        m_N = node_features.size();
        
        for(int i = 0; i < m_N; ++i){
            m_nodes[node_features[i].first] = node_features[i].second;
            for(const auto & xy : neighbors[i]){
                m_edges[node_features[i].first][xy.first] = xy.second;
            }
        }
    }
    
    std::vector<int> A_star_threshold(const int & start_node,
                                      const int & sink_node,
                                      const std::function<T2(T1, T1)> & heuristic_fct,
                                      const T2 & threshold,
                                      const std::function<bool(T2,T2)> & heur_comparison = std::greater<T2>()){
        
        int_T2_map      dists_from_start;              // Actual distance from start
        int_int_map     previous;
        int_T2_map      heurs_to_sink;                 // Heuristic distances to sink
        
        
        std::function<bool(int, int)> comparator = [& heurs_to_sink, & heur_comparison](int id_1, int id_2){
            return heur_comparison(heurs_to_sink[id_1], heurs_to_sink[id_2]);
            // Both heuristic distances will already have been computed
        };
        
        std::priority_queue<int, std::vector<int>, std::function<bool(int, int)> > active_nds (comparator);
        
        int_set active_nd_set;
        int_set closed_nd_set;
        
        // Just so comparison is defined for start node
        heurs_to_sink[start_node] = heuristic_fct(m_nodes[start_node],
                                                  m_nodes[sink_node]);
        dists_from_start[start_node] = 0;
        active_nds.push(start_node);
        
        int current_node;
        T2  current_dist;
        T2  heur_dist;
        T2  candidate_dist;
        
        while(! active_nds.empty()){
            current_node = active_nds.top();
            
            if(current_node == sink_node){
                return revert_path(sink_node, start_node, previous);
            }
            
            active_nds.pop();
            
            active_nd_set.erase(current_node);
            closed_nd_set.insert(current_node);
            
            current_dist = dists_from_start[current_node];
            
            for(const auto & xy : m_edges[current_node]){
                candidate_dist = current_dist + xy.second;
                
                if (candidate_dist > threshold) continue;
                
                if(heurs_to_sink.count(xy.first) == 0){
                    heurs_to_sink[xy.first] = candidate_dist +
                                                heuristic_fct(m_nodes[xy.first],
                                                              m_nodes[sink_node]);
                }
                heur_dist = heurs_to_sink[xy.first];
                
                if(candidate_dist + heur_dist > threshold) continue;
                
                if((dists_from_start.count(xy.first) == 0) // Never seen before
                   ||
                   (candidate_dist < dists_from_start[xy.first])){ // Better candidate
                    dists_from_start[xy.first] = candidate_dist;
                    previous[xy.first] = current_node;
                    if((closed_nd_set.count(xy.first) == 0) // Neighbor already in close set
                       &&
                       (active_nd_set.count(xy.first) == 0)){ // Neighbor already in active set
                        active_nds.push(xy.first);
                        active_nd_set.insert(xy.first);
                    }
                }
            }
            
        }
        
        return std::vector<int>();
        
    }
    
    void plot(){
        for(const auto & nd : m_nodes){
            std::cout << "Node: " << nd.first;
            std::cout << " (" << nd.second.first;
            std::cout << ", " << nd.second.second << "): ";
            for(const auto & edge : m_edges[nd.first]){
                std::cout << edge.first << " [" << edge.second << "], ";
            }
            std::cout << std::endl;
        }
        std::cout << std::endl;
    }
    
    
protected:
    
    std::vector<int> revert_path(int end_node, int start_node, int_int_map previous_nodes){
        std::vector<int> path = {end_node};
        int prev_node = previous_nodes[end_node];
        while(prev_node != start_node){
            path.push_back(prev_node);
            prev_node = previous_nodes[prev_node];
        }
        return path;
    }
    
    
    
};

#endif

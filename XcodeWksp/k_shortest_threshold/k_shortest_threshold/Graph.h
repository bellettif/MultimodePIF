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

#include "Edge_map.h"
#include "Reversion_map.h"
#include "Path.h"


typedef std::unordered_map<int, int>            int_int_map;
typedef std::unordered_map<int, int_int_map>    int_int_int_map_map;
typedef std::unordered_map<int, int_int_map>    int_int_int_map_map;
typedef std::set<int>                           int_set;
typedef std::unordered_map<int, int_set>        int_int_set_map;
typedef std::vector<int>                        int_vect;


template<typename T1, typename T2>
class Graph{
    
    typedef std::unordered_map<int, T1>             int_T1_map;
    typedef std::unordered_map<int, T2>             int_T2_map;
    typedef std::unordered_map<int, int_T2_map>     int_int_T2_map_map;
    typedef std::pair<T2, int_vect>                 T2_int_vect_pair;
    typedef std::vector<T2_int_vect_pair>           T2_int_vect_pair_vect;
    typedef std::unordered_map<int, Path<T2>*>      int_path_ptr_map;
    typedef std::unordered_map<int,
                                int_path_ptr_map>   int_int_path_ptr_map_map;
    
private:
    
    int_T1_map              m_nodes;
    Edge_map<T2>            m_edges;
    size_t                  m_N;

    
public:
    
    Graph(const std::vector< std::pair<int, T1> > & node_features,
          const std::vector< std::vector< std::pair<int, T2> > > & neighbors){
        
        assert(node_features.size() == neighbors.size());
        m_N = node_features.size();
        
        for(int i = 0; i < m_N; ++i){
            m_nodes[node_features[i].first] = node_features[i].second;
            for(const auto & xy : neighbors[i]){
                m_edges.add_edge(node_features[i].first, xy.first, xy.second);
            }
        }
    }
    
    /*
    @brief A star algorithm where the distance between start_node and sink_node is bounded
    by some threshold.
    @param start_node       Id of start node
    @param sink_node        Id of sink node
    @param heuristic_fct    Heuristic distance metric
    @param threshold        Maximum distance threshold
    @param heur_comparison  Comparison criterion for ordering heuristic distances
    @ret_val                Vector of ints that contains the series of points to sink_hole.
                            Empty if no valid path was found.
    */
    Path<T2>* A_star_threshold(const int & start_node,
                               const int & sink_node,
                               const std::function<T2(T1, T1)> & heuristic_fct,
                               const T2 & threshold,
                               const std::function<bool(T2,T2)> & heur_comparison = std::greater<T2>()){
        
        int_T2_map          dists_from_start;              // Actual distance from start
        Reversion_map       previous;
        int_T2_map          heurs_to_sink;                 // Heuristic distances to sink
        
        std::function<bool(int, int)> comparator = [& heurs_to_sink, & heur_comparison](int id_1, int id_2){
            return heur_comparison(heurs_to_sink[id_1], heurs_to_sink[id_2]);
            // Both heuristic distances will already have been computed
        };
        
        std::priority_queue<int,
                            std::vector<int>,
                            std::function<bool(int, int)> > active_nds (comparator);
        
        int_set active_nd_set;
        int_set closed_nd_set;
        
        // Just so comparison is defined for start node
        heurs_to_sink[start_node] = heuristic_fct(m_nodes[start_node],
                                                  m_nodes[sink_node]);
        dists_from_start[start_node] = 0;
        active_nds.push(start_node);
        
        int current_node;
        int dest_node;
        T2  current_dist;
        T2  heur_dist;
        T2  candidate_dist;
        
        while(! active_nds.empty()){
            current_node = active_nds.top();
            
            if(current_node == sink_node){
                return new Path<T2>(previous, m_edges,
                                    start_node, sink_node);
            }
            
            active_nds.pop();
            active_nd_set.erase(current_node);
            closed_nd_set.insert(current_node);
            
            current_dist = dists_from_start[current_node];
            
            for(const auto & node_dict_item : m_edges.get_edges(current_node)){
                
                dest_node = node_dict_item.first; // Other end of the edge
                candidate_dist = current_dist + node_dict_item.second;
                
                if (candidate_dist > threshold) continue;
                
                if(heurs_to_sink.count(dest_node) == 0){
                    heurs_to_sink[dest_node] = candidate_dist +
                    heuristic_fct(m_nodes[dest_node],
                                  m_nodes[sink_node]);
                }
                heur_dist = heurs_to_sink[dest_node];
                
                if(candidate_dist + heur_dist > threshold) continue;
                
                if((dists_from_start.count(dest_node) == 0) // Never seen before
                   ||
                   (candidate_dist < dists_from_start[dest_node])){ // Better candidate
                    dists_from_start[dest_node] = candidate_dist;
                    previous.rev_dict[dest_node] = current_node;
                    if((closed_nd_set.count(dest_node) == 0) // Neighbor already in close set
                       &&
                       (active_nd_set.count(dest_node) == 0)){ // Neighbor already in active set
                        active_nds.push(dest_node);
                        active_nd_set.insert(dest_node);
                    }
                }
            }
            
        }
        
        return new Path<T2>();
        
    }
    
    
    /*
    Yen's algorithm with threshold modification
    */
    std::vector<Path<T2>*> k_shortest_threshold(const T2 & threshold,
                                               unsigned int K,
                                               int start_node,
                                               int sink_node,
                                               const std::function<T2(T1, T1)> & heuristic_fct,
                                               const std::function<bool(T2,T2)> & heur_comparison = std::greater<T2>()){
        
        /*
         Set up
         */
        // Keep track of spur costs
        std::function<bool(std::tuple<int, int, T2>,
                           std::tuple<int, int, T2>)> comparator =
                                [](std::tuple<int, int, T2> x,
                                   std::tuple<int, int, T2> y){
            return x > y;
        };
        std::priority_queue<std::tuple<int, int, T2>,
                            std::vector<std::tuple<int, int, T2>>,
                            std::function<bool(std::tuple<int, int, T2>,
                                               std::tuple<int, int, T2>)>> cost_record (comparator);
        int_int_path_ptr_map_map    candidate_map;
        std::vector<Path<T2>*>      result;
        int_int_set_map             path_edge_map;      // Keep track of edges on paths
        int                         prev_spur_index         = 1;
        int                         best_k;
        int                         best_i;
        int                         source_to_rm;
        int                         dest_to_rm;
        int_vect                    buffer;
        Path<T2> *                  candidate               = nullptr;
        Path<T2> *                  best_candidate          = nullptr;
        int_int_T2_map_map          removed_edges;
        int_T1_map                  removed_nodes;
        
        
        /*
         Initialize
         */
        result.push_back(A_star_threshold(start_node,
                                          sink_node,
                                          heuristic_fct,
                                          threshold));
        if(result[0]->empty()){ // The shortest path is already above the threshold
            delete result[0];
            result.clear();
            return result;
        }else{
            source_to_rm = result[0]->get_node(0);
            dest_to_rm   = result[0]->get_node(1);
            removed_edges[source_to_rm][dest_to_rm] =
                m_edges.remove_edge(source_to_rm, dest_to_rm);
            removed_nodes[source_to_rm] = remove_node(source_to_rm, removed_edges);
        }
        
        /*
         Run
         */
        for(int k_it = 0; k_it < K - 1; ++k_it){
            
            const std::vector<int> & path_ids = result.back()->get_ids();
            /*
             Compute new spurs' costs
            */
            for(int i = prev_spur_index; i < path_ids.size() - 1; ++i){
                
                source_to_rm = path_ids.at(i);
                for(auto const & d : path_edge_map[source_to_rm]){
                    removed_edges[source_to_rm][d] =
                        m_edges.remove_edge(source_to_rm, d);
                }
                
                candidate = A_star_threshold(path_ids.at(i),
                                             sink_node,
                                             heuristic_fct,
                                             threshold);
                if(candidate->empty()){
                    delete candidate;
                    continue;
                }
                
                candidate->concatenate_front(*(result.back()), i);
                cost_record.push({k_it, i, candidate->get_cost()});
                candidate_map[k_it][i] = candidate;
                
                removed_nodes[source_to_rm] = remove_node(source_to_rm, removed_edges);
                
            }
            if(cost_record.empty()){
                return result;
            }
            
            /*
             Select best candidate
            */
            best_k = std::get<0>(cost_record.top());
            best_i = std::get<1>(cost_record.top());
            best_candidate = candidate_map[best_k][best_i];
            cost_record.pop();
            candidate_map[best_k].erase(best_i);
            /*
             Restore state of the graph
            */
            // Add back the edges that had been deleted
            for(auto const & xyz : removed_edges){
                for(auto const & yz : xyz.second){
                    m_edges.add_edge(xyz.first,
                                     yz.first,
                                     yz.second);
                }
            }
            removed_edges.clear();
            // Add back the nodes that had been delete
            for(auto const & xy : removed_nodes){
                m_nodes[xy.first] = xy.second;
            }
            removed_nodes.clear();
            
            std::cout << "Cost before concatenation = " << best_candidate->get_cost() << std::endl;
            
            std::cout << "Cost after concatenation = " << best_candidate->get_cost() << std::endl;
            
            result.push_back(best_candidate);
            
            path_edge_map[result[best_k]->get_node(best_i)].insert(best_candidate->get_node(1));

        }
        
        for(const auto & xyz : candidate_map){
            for(const auto & yz : xyz.second){
                delete candidate_map[xyz.first][yz.first];
            }
        }
        
        return result;
    }
    
    void plot(){
        for(const auto & nd : m_nodes){
            std::cout << "Node: " << nd.first;
            std::cout << " (" << nd.second.first;
            std::cout << ", " << nd.second.second << "): ";
            for(const auto & xy : m_edges.get_edges(nd.first)){
                std::cout << xy.first << " [" << xy.second << "] ";
            }
            std::cout << std::endl;
        }
        std::cout << std::endl;
    }
    
    
public:
    
    /*
    Get a path from start_node to end_node with the trace of previous nodes
    */
    std::vector<int> revert_path(int end_node, int start_node, int_int_map previous_nodes){
        std::vector<int> path = {end_node};
        int prev_node = previous_nodes[end_node];
        while(prev_node != start_node){
            path.push_back(prev_node);
            prev_node = previous_nodes[prev_node];
        }
        path.push_back(start_node);
        std::reverse(path.begin(), path.end());
        return path;
    }
    
    T2 remove_edge(int origin, int dest){
        return m_edges.remove_edge(origin, dest);
    }
    
    T1 remove_node(int node_id, int_int_T2_map_map & removed_edges){
        T1 buffer = m_nodes[node_id];
        auto to_remove_dict (m_edges.get_edges(node_id));
        for(const auto & xy : to_remove_dict){
            removed_edges[node_id][xy.first] = m_edges.remove_edge(node_id, xy.first);
        }
        m_nodes.erase(node_id);
        return buffer;
    }
    
    void add_node(int node_id, T1 feature){
        m_nodes[node_id] = feature;
    }
    
    void add_edge(int origin, int dest, T2 feature){
        m_edges.add_edge(origin, dest, feature);
    }
    
};

#endif

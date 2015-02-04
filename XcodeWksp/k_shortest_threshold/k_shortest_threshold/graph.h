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
#include <algorithm>

#include "edge_map.h"
#include "reversion_map.h"
#include "path.h"


typedef std::unordered_map<long, long>              long_long_map;
typedef std::unordered_map<long, long_long_map>     long_long_long_map_map;
typedef std::unordered_map<long, long_long_map>     long_long_long_map_map;
typedef std::set<long>                              long_set;
typedef std::unordered_map<long, long_set>          long_long_set_map;
typedef std::vector<long>                           long_vect;


template<typename T1, typename T2>
class Graph{
    
    typedef std::unordered_map<long, T1>             long_T1_map;
    typedef std::unordered_map<long, T2>             long_T2_map;
    typedef std::unordered_map<long, long_T2_map>    long_long_T2_map_map;
    typedef std::pair<T2, long_vect>                 T2_long_vect_pair;
    typedef std::vector<T2_long_vect_pair>           T2_long_vect_pair_vect;
    typedef std::unordered_map<int, Path<T2>*>       int_path_ptr_map;
    typedef std::unordered_map<int,
                               int_path_ptr_map>     int_int_path_ptr_map_map;
    
private:
    
    long_T1_map             m_nodes;
    Edge_map<T2>            m_edges;
    size_t                  m_N;

    
public:
    
    Graph(const std::vector< std::pair<long, T1> > & node_features,
          const std::vector< std::vector< std::pair<long, T2> > > & neighbors){
        
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
    Path<T2>* A_star_threshold(const long & start_node,
                               const long & sink_node,
                               const std::function<T2(T1, T1)> & heuristic_fct,
                               const T2 & threshold,
                               const std::function<bool(T2,T2)> & heur_comparison = std::greater<T2>()){
        
        long_T2_map          dists_from_start;              // Actual distance from start
        Reversion_map        previous;
        long_T2_map          heurs_to_sink;                 // Heuristic distances to sink
        
        std::function<bool(long, long)> comparator = [& heurs_to_sink, & heur_comparison](long id_1, long id_2){
            return heur_comparison(heurs_to_sink[id_1], heurs_to_sink[id_2]);
            // Both heuristic distances will already have been computed
        };
        
        std::priority_queue<long,
                            std::vector<long>,
                            std::function<bool(long, long)> > active_nds (comparator);
        
        long_set active_nd_set;
        long_set closed_nd_set;
        
        // Just so comparison is defined for start node
        heurs_to_sink[start_node] = heuristic_fct(m_nodes[start_node],
                                                  m_nodes[sink_node]);
        dists_from_start[start_node] = 0;
        active_nds.push(start_node);
        
        long current_node;
        long dest_node;
        T2   current_dist;
        T2   heur_dist;
        T2   candidate_dist;
        
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
            
            //std::cout << "Graph getting edges for " << current_node << std::endl;
            for(const auto & node_dict_item : m_edges.get_edges(current_node)){
                //std::cout << "Graph done getting edges for " << current_node << std::endl;
                
                dest_node = node_dict_item.first; // Other end of the edge
                //std::cout << "Dest node = " << dest_node << std::endl;
                candidate_dist = current_dist + node_dict_item.second;
                
                if (candidate_dist > threshold) continue;
                
                heur_dist = heuristic_fct(m_nodes[dest_node],
                                          m_nodes[sink_node]) + candidate_dist;
                
                if(heurs_to_sink[dest_node] <  heur_dist){
                    heurs_to_sink[dest_node] = heur_dist;
                }
                
                if(heur_dist > threshold) continue;
                
                if ((dists_from_start.count(dest_node) == 0) || // Never seen before
                    (candidate_dist < dists_from_start[dest_node])) { // Better candidate
                    dists_from_start[dest_node] = candidate_dist;
                    heurs_to_sink[dest_node] = candidate_dist + heuristic_fct(m_nodes[dest_node],
                                                                              m_nodes[sink_node]);
                    previous.rev_dict[dest_node] = current_node;
                    if((closed_nd_set.count(dest_node) == 0) &&// Neighbor already in close set
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
                                               long start_node,
                                               long sink_node,
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
            return x < y;
        };
        std::priority_queue<std::tuple<int, int, T2>,
                            std::vector<std::tuple<int, int, T2>>,
                            std::function<bool(std::tuple<int, int, T2>,
                                               std::tuple<int, int, T2>)>> cost_record (comparator);
        int_int_path_ptr_map_map    candidate_map;
        std::vector<Path<T2>*>      result;
        int                         prev_spur_index         = 0;
        int                         best_k;
        int                         best_i;
        long                        source_to_rm;
        long                        dest_to_rm;
        long_vect                   buffer;
        Path<T2> *                  candidate               = nullptr;
        Path<T2> *                  best_candidate          = nullptr;
        long_long_T2_map_map        removed_edges;
        long_T1_map                 removed_nodes;
        
        
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
        }
        
        //result.front()->plot();
        
        /*
         Run
         */
        for(int k_it = 0; k_it < K - 1; ++k_it){
            
            //std::cout << "k_it = " << k_it << std::endl;
            
            const std::vector<long> & path_ids = result.back()->get_ids();
            /*
             Compute new spurs' costs
            */
            //std::cout << "-------------" << std::endl;
            //std::cout << prev_spur_index << std::endl;
            //std::cout << path_ids.size() << std::endl;
            for(int i = 0; i < prev_spur_index; ++i){
                //std::cout << "Shout 1" << std::endl;
                long temp = path_ids.at(i);
                removed_nodes[path_ids.at(i)] = remove_node(path_ids.at(i), removed_edges);
                //std::cout << "Echo 1" << std::endl;
            }
            for(int i = prev_spur_index; i < path_ids.size() - 1; ++i){
                
                //std::cout << "Shout 2" << std::endl;
                source_to_rm    =   path_ids.at(i);
                dest_to_rm      =   path_ids.at(i+1);
                //std::cout << "Echo 2" << std::endl;
                if(m_edges.contains_edge(source_to_rm, dest_to_rm)){
                    removed_edges[source_to_rm][dest_to_rm] =
                        m_edges.remove_edge(source_to_rm, dest_to_rm);
                    //std::cout << "Deleted edge " << source_to_rm << "->" << dest_to_rm << std::endl;
                }
                
                for(int j = 0; j < result.size() - 1; ++j){
                    if(result[j]->contains(*(result.back()), i)){
                        dest_to_rm = result[j]->get_node(i + 1);
                        if(m_edges.contains_edge(source_to_rm, dest_to_rm)){
                            removed_edges[source_to_rm][dest_to_rm] =
                                m_edges.remove_edge(source_to_rm, dest_to_rm);
                                //std::cout << "Deleted edge " << source_to_rm << "->" << dest_to_rm << std::endl;
                        }
                    }
                }
                
                candidate = A_star_threshold(path_ids.at(i),
                                             sink_node,
                                             heuristic_fct,
                                             threshold);
                if(candidate->empty()){
                    //std::cout << "------------------" << std::endl;
                    //std::cout << "No valid candidate" << std::endl;
                    //std::cout << "------------------" << std::endl;
                    delete candidate;
                    continue;
                }
                
                //std::cout << "---------------" << std::endl;
                //std::cout << "Valid candidate" << std::endl;
                //std::cout << "---------------" << std::endl;
                
                //std::cout << "-------------------" << std::endl;
                //candidate->plot();
                //result.back()->plot();
                
                //std::cout << "\t" << i << std::endl;
                //std::cout << "\t" << candidate->size() << std::endl;
                
                //std::cout << "Executing concatenate front" << std::endl;
                candidate->concatenate_front_(*(result.back()), i);
                //std::cout << "Done executing concatenate front" << std::endl;
                
                //std::cout << "\t" << candidate->size() << std::endl;
                
                //candidate->plot();
                
                std::tuple<long, long, double> temp (k_it, i, candidate->get_cost());
                cost_record.push(temp);
                
                //std::cout << "\t" << candidate->size() << std::endl;
                
                //std::cout << candidate->size() <<  " " << i << std::endl;
                
                candidate_map[k_it][i] = candidate;
                
                //candidate->plot();
                //std::cout << "-------------------" << std::endl;
                
                if(m_nodes.count(source_to_rm)){
                    removed_nodes[source_to_rm] = remove_node(source_to_rm, removed_edges);
                    //std::cout << "Deleted node " << source_to_rm << std::endl;
                };
             
            }
            
            if(cost_record.empty()){
                return result;
            }
            
            /*
             Select best candidate
            */
            best_k = std::get<0>(cost_record.top());
            best_i = std::get<1>(cost_record.top());
            //std::cout << "-------------------------" << std::endl;
            //std::cout << "Best k = " << best_k << ", best i = " << best_i << std::endl;
            best_candidate = candidate_map[best_k][best_i];
            //std::cout << "Best cost = " << best_candidate->get_cost() << std::endl;
            //std::cout << "-------------------------" << std::endl;
            cost_record.pop();
            candidate_map[best_k].erase(best_i);
            prev_spur_index = best_i;
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
            
            result.push_back(best_candidate);

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
    std::vector<long> revert_path(long end_node, long start_node, long_long_map previous_nodes){
        std::vector<long> path = {end_node};
        long prev_node = previous_nodes[end_node];
        while(prev_node != start_node){
            path.push_back(prev_node);
            prev_node = previous_nodes[prev_node];
        }
        path.push_back(start_node);
        std::reverse(path.begin(), path.end());
        return path;
    }
    
    T2 remove_edge(long origin, long dest){
        return m_edges.remove_edge(origin, dest);
    }
    
    T1 remove_node(long node_id, long_long_T2_map_map & removed_edges){
        T1 buffer = m_nodes[node_id];
        //std::cout << "Graph fetching node for removal" << std::endl;
        auto to_remove_dict (m_edges.get_edges(node_id));
        //std::cout << "Graph done fetching node for removal" << std::endl;
        for(const auto & xy : to_remove_dict){
            removed_edges[node_id][xy.first] = m_edges.remove_edge(node_id, xy.first);
        }
        m_nodes.erase(node_id);
        return buffer;
    }
    
    void add_node(long node_id, T1 feature){
        m_nodes[node_id] = feature;
    }
    
    void add_edge(long origin, long dest, T2 feature){
        m_edges.add_edge(origin, dest, feature);
    }
    
};

#endif

//
//  Header.h
//  k_shortest_threshold
//
//  Created by francois.belletti on 1/29/15.
//  Copyright (c) 2015 francois.belletti. All rights reserved.
//

#ifndef k_shortest_threshold_Edge_map_h
#define k_shortest_threshold_Edge_map_h

#include <unordered_map>
#include <set>
#include <vector>

typedef std::unordered_map<int, int>                    int_int_map;
typedef std::unordered_map<int, int_int_map>            int_int_int_map;

template<typename T>
class Edge_map{
    
    typedef std::unordered_map<int, T>                  T_map;
    typedef std::unordered_map<int, T_map>              int_T_map_map;
    typedef std::unordered_map<int, int_T_map_map>      int_int_T_map_map;
    
    
private:
    int_int_T_map_map  m_edges;
    int_int_int_map     m_n_edges;

    
public:
    
    inline const int_T_map_map & get_edges(int node) const{
        return m_edges.at(node);
    }
    
    inline const T_map & get_edges(int start, int dest) const{
        return m_edges.at(start).at(dest);
    }
    
    inline void add_edge(int start, int dest, const T & feature){
        int n_edges = m_n_edges[start][dest];
        m_edges[start][dest][n_edges + 1] = feature;
        m_n_edges[start][dest] ++;
    }
    
    inline void add_edge(int start, int dest, int edge_id, const T & feature){
        m_edges[start][dest][edge_id] = feature;
        m_n_edges[start][dest] ++;
    }

    inline T remove_edge(int start, int dest, int edge_id){
        T temp = m_edges[start][dest][edge_id];
        m_edges[start][dest].erase(edge_id);
        m_n_edges[start][dest] --;
        return temp;
    }
    
};

#endif

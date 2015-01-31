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


template<typename T>
class Edge_map{
    
    typedef std::unordered_map<int, T>                  T_map;
    typedef std::unordered_map<int, T_map>              int_T_map_map;
    
    
private:
    int_T_map_map  m_edges;
    
    
public:
    
    inline const T_map & get_edges(int node) const{
        return m_edges.at(node);
    }
    
    inline const T & get_edge(int origin, int dest) const{
        return m_edges.at(origin).at(dest);
    }
    
    inline void add_edge(int start, int dest, const T & feature){
        m_edges[start][dest] = feature;
    }

    inline T remove_edge(int start, int dest){
        T temp = m_edges[start][dest];
        m_edges[start].erase(dest);
        return temp;
    }
    
};

#endif

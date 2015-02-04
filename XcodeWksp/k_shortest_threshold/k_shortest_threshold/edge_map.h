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

typedef std::unordered_map<long, long>                  long_long_map;


template<typename T>
class Edge_map{
    
    typedef std::unordered_map<long, T>                  T_map;
    typedef std::unordered_map<long, T_map>              long_T_map_map;
    
    
private:
    long_T_map_map  m_edges;
    
    
public:
    
    inline const T_map & get_edges(long node) const{
        return m_edges.at(node);
    }
    
    inline const T & get_edge(long origin, long dest) const{
        return m_edges.at(origin).at(dest);
    }
    
    inline void add_edge(long start, long dest, const T & feature){
        m_edges[start][dest] = feature;
    }

    inline bool contains_edge(long start, long dest){
        if(m_edges.count(start)){
            if(m_edges.at(start).count(dest)){
                return true;
            }
        }
        return false;
    }
    
    inline T remove_edge(long start, long dest){
        T temp = m_edges[start][dest];
        m_edges[start].erase(dest);
        return temp;
    }
    
};

#endif

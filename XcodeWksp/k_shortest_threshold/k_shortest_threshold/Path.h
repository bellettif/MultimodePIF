//
//  Path.h
//  k_shortest_threshold
//
//  Created by francois.belletti on 1/29/15.
//  Copyright (c) 2015 francois.belletti. All rights reserved.
//

#ifndef k_shortest_threshold_Path_h
#define k_shortest_threshold_Path_h

#include <vector>
#include <iostream>

#include "Reversion_map.h"


template<typename T>
class Path{
    
private:
    
    std::vector<std::pair<int, int>>    m_ids;
    int                                 m_end;
    T                                   m_cost      = 0;
    

public:
    Path(){
        
    }
    
    Path(const Reversion_map & rev_map, int start_id, int sink_id){
        m_end = sink_id;
        int current_nd_id = sink_id;
        while(current_nd_id != start_id){
            m_ids.push_back(rev_map.rev_dict.at(current_nd_id));
            current_nd_id = rev_map.rev_dict.at(current_nd_id).first;
        }
        std::reverse(m_ids.begin(), m_ids.end());
    }

    void add(int node_id, int edge_id, const T & edge_cost){
        m_ids.emplace_back({node_id, edge_id});
        m_cost += edge_cost;
    }
    
    const std::vector<std::pair<int, int>> & get_ids() const{
        return m_ids;
    }
    
    int get_node(int i) const{
        return m_ids[i].first;
    }
    
    int get_edge(int i) const{
        return m_ids[i].second;
    }
    
    const T & get_cost() const{
        return m_cost;
    }

    bool empty() const{
        return (m_ids.size() == 0);
    }

    void plot() const{
        std::cout << "Total cost = " << m_cost << std::endl;
        for(auto const & x : m_ids){
            std::cout << x.first << " -" << x.second << "-> ";
        }
        std::cout << m_end << std::endl;
    }

    void concatenate_front(const Path<T> & other_path){
        std::vector<std::pair<int, int>> temp (other_path.get_ids());
        for(const auto & x : m_ids){
            temp.push_back(x);
        }
        m_ids.swap(temp);
    }
    
};


#endif

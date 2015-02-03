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
#include <string>
#include <set>
#include <algorithm>

#include "reversion_map.h"
#include "edge_map.h"


template<typename T>
class Path{
    
public:
    
    std::vector<int>            m_ids;
    T                           m_cost          = 0;
    std::vector<T>              m_partial_costs;
    std::set<std::string>       m_signature_set;
    std::vector<std::string>    m_partial_signatures;

public:
    Path(){
        
    }
    
    Path(const Reversion_map & rev_map,
         const Edge_map<T> & edge_map,
         int start_id,
         int sink_id){
        
        int current_nd_id = sink_id;
        
        m_ids.push_back(sink_id);
        
        while(current_nd_id != start_id) {
            
            const auto & temp = rev_map.rev_dict.at(current_nd_id);
            m_ids.push_back(temp);
            const T & edge_cost = edge_map.get_edge(temp,
                                                    current_nd_id);
            m_partial_costs.push_back(edge_cost);
            m_cost += edge_cost;
            
            current_nd_id = temp;
        }
        
        std::reverse(m_ids.begin(), m_ids.end());
        std::reverse(m_partial_costs.begin(), m_partial_costs.end());
        
        for(int i = 1; i < m_partial_costs.size(); ++i){
            m_partial_costs[i] += m_partial_costs[i-1];
        }
        
        compute_signatures();
        
    }

    void add(int node_id, const T & edge_cost){
        m_ids.push_back(node_id);
        m_cost += edge_cost;
        
    }
    
    const std::vector<int> & get_ids() const{
        return m_ids;
    }
    
    int get_node(int i) const{
        return m_ids.at(i);
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
            std::cout << x << "-> ";
        }
        std::cout << std::endl;
        for(auto const & x : m_partial_costs){
            std::cout << x << "-> ";
        }
        std::cout << std::endl;
    }

    void concatenate_front(const Path<T> & other_path){
        
        std::vector<int> temp (other_path.m_ids);
        
        m_partial_signatures    =   other_path.m_partial_signatures;
        m_signature_set         =   other_path.m_signature_set;
        m_cost                  +=  other_path.m_cost;

        m_partial_costs.insert(m_partial_costs.begin(),
                               other_path.m_partial_costs.begin(),
                               other_path.m_partial_costs.end());
        size_t offset = other_path.m_partial_costs.size();
        for(size_t i = offset; i < m_partial_costs.size(); ++i){
            m_partial_costs[i] += other_path.m_cost;
        }
        
        std::string current_signature (m_partial_signatures.back());
        
        for(const auto & x : m_ids){
            temp.push_back(x);
            current_signature += x;
            m_signature_set.insert(current_signature);
            m_partial_signatures.push_back(current_signature);
        }
        m_ids.swap(temp);
        
    }
    
    void concatenate_front(const Path<T> & other_path, int spur_idx){
        
        m_ids.insert(m_ids.begin(),
                     other_path.m_ids.begin(),
                     other_path.m_ids.begin() + spur_idx);
        
        m_partial_costs.insert(m_partial_costs.begin(),
                               other_path.m_partial_costs.begin(),
                               other_path.m_partial_costs.begin() + spur_idx);
        int offset = spur_idx;
        int partial_cost;
        if(spur_idx > 0){
            partial_cost = m_partial_costs[spur_idx - 1];
        }else{
            partial_cost = 0;
        }
        m_cost += partial_cost;
        for(int i = offset; i < m_partial_costs.size(); ++i){
            m_partial_costs[i] += partial_cost;
        }
        
        m_partial_signatures.clear();
        m_partial_signatures.insert(m_partial_signatures.begin(),
                                    other_path.m_partial_signatures.begin(),
                                    other_path.m_partial_signatures.begin() + spur_idx);
        
        compute_signatures();
    }
    
    int size() const{
        return m_ids.size();
    }
    
    bool contains(const Path<T> & other_path, int spur_idx) const{
        return m_signature_set.count(other_path.m_partial_signatures.at(spur_idx));
    }
    
    
private:
    
    void compute_signatures(){
        std::string current_signature = "";
        for(const auto & x : m_ids){
            current_signature += x;
            m_signature_set.insert(current_signature);
            m_partial_signatures.push_back(current_signature);
        }
    }
    
};


#endif

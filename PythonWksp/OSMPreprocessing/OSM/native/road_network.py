'''
Created on Jan 5, 2015

@author: Francois Belletti
'''

def reduce_network(linked_nodes):
    to_delete = []
    for node_id, neighbours in linked_nodes.iteritems():
        if len(neighbours) == 2:
            neigh_items = neighbours.items()
            left_neigh  , left_features  = neigh_items[0]
            right_neigh , right_features = neigh_items[1]
            #    Check that properties are identical
            left_speed  = left_features['max_speed']
            left_type   = left_features['highway_type']
            right_speed = right_features['max_speed']
            right_type  = right_features['highway_type']
            if((left_speed == right_speed) and 
               (left_type  == right_type)):
                # Collapse node with node_id into neighbours
                tot_length = left_features['length'] + \
                             right_features['length']
                #if (left_neigh not in linked_nodes[right_neigh]) \
                #    and (right_neigh not in linked_nodes[left_neigh]):
                linked_nodes[right_neigh][left_neigh] = \
                    {'length'       : tot_length,
                     'highway_type' : left_type,
                     'max_speed'    : left_speed}
                del linked_nodes[right_neigh][node_id]
                linked_nodes[left_neigh][right_neigh] = \
                    {'length'       : tot_length,
                     'highway_type' : left_type,
                     'max_speed'    : left_speed}
                del linked_nodes[left_neigh][node_id]
                to_delete.append(node_id)
    for node_id in to_delete:
        del linked_nodes[node_id]
                
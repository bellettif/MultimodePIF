'''
Created on Jan 5, 2015

@author: Francois Belletti
'''

import numpy as np

#
#    Need to change that distance
#
def l2_dist(node_1, node_2):
    lat_1 = float(node_1.get('lat'))
    lon_1 = float(node_1.get('lon'))
    lat_2 = float(node_2.get('lat'))
    lon_2 = float(node_2.get('lon'))
    return np.sqrt((lat_1 - lat_2) ** 2 + (lon_1 - lon_2) ** 2)

#
#    Extract a given target network (road, rail, subway)
#        from a list of ways as well as the references
#        to all nodes (as a dict)
#    Returns the edges as a list, the nodes as the keys
#        of a dict recaping all their parents
#
def extract_edges(ways, target_key, target_values):
    node_seqs = []
    node_refs = {}
    #
    for way in ways:
        ref_tags  = way.findall('tag')
        in_network = False
        for ref_tag in ref_tags:
            k = ref_tag.get('k')
            v = ref_tag.get('v')
            if k == target_key and v in target_values:
                in_network = True
                break
        if not in_network:
            continue
        else:
            node_seqs.append(way)
        way_id = way.get('id')
        child_nodes = way.findall('nd')
        for child_node in child_nodes:
            node_id = child_node.get('ref')
            if node_id not in node_refs:
                node_refs[node_id] = []
            node_refs[node_id].append(way_id)
    return node_seqs, node_refs
    
#
#    Split ways into links between intersections
#
def split_ways(node_seqs, node_refs, node_dict, target_features):
    #    Convenience compute distance function
    def cmpt_length(node_seq):
        dist = 0
        for i in range(len(node_seq) - 1):
            prev_node = node_dict[node_seq[i].get('ref')]
            next_node = node_dict[node_seq[i+1].get('ref')]
            dist += l2_dist(prev_node, next_node)
        return dist
    #
    all_features = ['length', 'node_seq']
    all_features.extend(target_features)
    #
    links = []
    for node_seq in node_seqs:
        features = dict.fromkeys(target_features, None)
        for tag in node_seq.findall('tag'):
            k = tag.get('k')
            if k not in features:
                continue
            v = tag.get('v')
            features[k] = v
        node_seq = node_seq.findall('nd')
        ref_seq = [len(node_refs[x.get('ref')]) for x in node_seq]
        cut_indices = []
        ref_seq_len = len(ref_seq)
        for i, n_ref in enumerate(ref_seq):
            if n_ref > 1 and (i != 0) and (i != (ref_seq_len - 1)):
                cut_indices.append(i)
        sub_links = []
        cut_indices_len = len(cut_indices)
        #    For factoring
        def sub_seq_summary(sub_sequence):
            sub_seq_length = cmpt_length(sub_sequence)
            summary = dict.fromkeys(all_features, None)
            summary['length']   = sub_seq_length # in meters
            summary['node_seq'] = sub_sequence
            for feature in target_features:
                summary[feature] = features[feature]
            return summary
        #
        if cut_indices_len > 0:
            for i, cut_index in enumerate(cut_indices):
                if i == 0:
                    sub_seq = node_seq[:cut_index + 1]  # reach for 1 more to create overlap
                    sub_links.append(sub_seq_summary(sub_seq))
                if i < (cut_indices_len - 1):
                    sub_seq = node_seq[cut_index:cut_indices[i+1] + 1]
                    sub_links.append(sub_seq_summary(sub_seq))
                if i == (cut_indices_len - 1):
                    sub_seq = node_seq[cut_index:]
                    sub_links.append(sub_seq_summary(sub_seq))
        else:
            sub_seq = node_seq
            sub_links = [sub_seq_summary(sub_seq)]
        links.extend(sub_links)
    return links

#        
#    From the links (dual graph) build the nodes and link
#        them one to another (primal graph)
#    The result is a dict[node] = [neighbours]
#
def link_nodes(links, target_features):
    linked_nodes = {}
    for link in links:
        leftmost_node_id  = link['node_seq'][0].get('ref')
        rightmost_node_id = link['node_seq'][-1].get('ref')
        # The following work on the set of features
        #     needs to become dynamic
        edge_dict = {}
        edge_dict['length'] = link['length']
        for feature in target_features:
            edge_dict[feature] = link[feature]
        #
        #    Create edges in graph (vertices are keys)
        #    So far one ways are not taken into account
        #
        # Link left to right
        if leftmost_node_id not in linked_nodes:
            linked_nodes[leftmost_node_id] = {}
        linked_nodes[leftmost_node_id][rightmost_node_id] = \
            edge_dict
        # Link right to left
        if rightmost_node_id not in linked_nodes:
            linked_nodes[rightmost_node_id] = {}
        linked_nodes[rightmost_node_id][leftmost_node_id] = \
            edge_dict
    return linked_nodes
            
#
#    Reduce network for routing applications, get rid of
#        nodes that do not correspond to intersections
#
def reduce_network(linked_nodes,
                   feature_list):
    to_delete = []
    for node_id, neighbours in linked_nodes.iteritems():
        if len(neighbours) == 2:
            neigh_items = neighbours.items()
            left_neigh  , left_features  = neigh_items[0]
            right_neigh , right_features = neigh_items[1]
            #    Check that properties are identical
            identical = True
            for feature in feature_list:
                if left_features[feature] != right_features[feature]:
                    identical = False
            if not identical:
                continue
            # Collapse node with node_id into neighbours
            tot_length = left_features['length'] + \
                         right_features['length']
            merge_features = {}
            merge_features['length'] = tot_length
            for feature in feature_list:
                merge_features[feature] = left_features[feature]
            #
            linked_nodes[right_neigh][left_neigh] = merge_features
            del linked_nodes[right_neigh][node_id]
            #
            linked_nodes[left_neigh][right_neigh] = merge_features
            del linked_nodes[left_neigh][node_id]
            #
            to_delete.append(node_id)
    for node_id in to_delete:
        del linked_nodes[node_id]
               
                
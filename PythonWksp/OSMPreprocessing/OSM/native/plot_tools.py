'''
Created on Jan 5, 2015

@author: Francois Belletti
'''

HIGHWAY_COLORS = {'primary'   : 'red',
                  'secondary' : 'blue',
                  'tertiary'  : 'green'}

def plot_network(node_dict, linked_nodes, ax):
    for node_id, neighbours in linked_nodes.iteritems():
        node_lat = node_dict[node_id].get('lat')
        node_lon = node_dict[node_id].get('lon')
        for neigh_id, features in neighbours.iteritems():
            neigh_lat = node_dict[neigh_id].get('lat')
            neigh_lon = node_dict[neigh_id].get('lon')
            ax.plot([node_lon, neigh_lon], [node_lat, neigh_lat],
                    c = HIGHWAY_COLORS[features['highway_type']])
            ax.scatter([node_lon, neigh_lon], [node_lat, neigh_lat],
                    c = HIGHWAY_COLORS[features['highway_type']])